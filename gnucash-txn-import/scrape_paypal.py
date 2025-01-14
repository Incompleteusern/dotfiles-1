from datetime import date as _date
from datetime import datetime, timedelta
from decimal import Decimal
from pprint import pprint
from typing import Any

from bs4 import BeautifulSoup

today = _date.today

from gnucash_api import TxnAddArgsDict, get_account, get_session, to_dollars


def get_child_string(div: BeautifulSoup, tag_name="span", cy: str | None = None) -> str:
    if cy is None:
        elm = div.find(tag_name)
    else:
        elm = div.find(tag_name, attrs={"data-cy": cy})
    assert elm is not None, f"Couldn't find {tag_name} with data-cy={cy} in {div}"
    return " ".join(line.strip() for line in elm.strings if line.strip()).strip()


current_year = int(datetime.today().strftime("%Y"))
assert current_year > 2000

rows_for_csv: list[Any] = []

with get_session() as session:
    paypal = get_account(session, "A:Paypal")
    recent_txn = [
        txn for txn in paypal.transactions if txn.date >= today() + timedelta(days=-70)
    ]
    args_txn_to_create: list[TxnAddArgsDict] = []

    with open("/home/evan/dotfiles/gnucash-txn-import/data/paypal.html") as htmlfile:
        soup = BeautifulSoup(htmlfile, features="lxml")

    for div in soup.find_all("div", role="button"):
        str_amount = get_child_string(div, cy="totalAmountTextVal")
        str_amount = str_amount.replace("$", "")
        str_amount = str_amount.replace(" ", "")
        row_amount = to_dollars(str_amount)
        str_date = get_child_string(div, cy="dateText")
        row_date = datetime.strptime(f"{str_date} {current_year}", r"%b %d %Y").date()
        if row_date > _date.today():
            row_date = datetime.strptime(
                f"{str_date} {current_year-1}", r"%b %d %Y"
            ).date()
        row_description = get_child_string(div, tag_name="div", cy="counterpartyName")
        try:
            note = get_child_string(div, tag_name="div", cy="notes")
        except AssertionError:
            note = ""
        else:
            note = note.strip('"')
            if len(note) > 52:
                note = note[:48] + "..."
            row_description += ": " + note

        if row_date < today() + timedelta(days=-60):
            continue
        rows_for_csv.append([row_description, row_amount, row_date])

        for txn in recent_txn:
            if (
                abs(row_date - txn.date) <= timedelta(days=1)
                and row_amount == txn.amount
            ):
                print(f"Handled {row_description} from {row_date}")
                break
        else:
            if (
                row_amount in (Decimal("-17.64"), Decimal("-31.36"), Decimal("-40.96"))
                and ": OTIS" in row_description
            ):
                account_name = "E:Work:Intern"
            else:
                account_name = "Orphan-USD"
            args_txn_to_create.append(
                {
                    "amount": row_amount,
                    "description": row_description,
                    "target": get_account(session, account_name),
                    "txn_date": row_date,
                }
            )

    pprint(args_txn_to_create)
    if len(args_txn_to_create) > 0:
        user_response = input("Continue? [y/n]: ").lower().strip()
        if user_response.startswith("y") or user_response == "":
            for args_dict in args_txn_to_create:
                paypal.add(**args_dict)

with open("data/auto-gen-paypal.csv", "w") as f:
    print("description,amount,date", file=f)
    for row in rows_for_csv:
        print(",".join(str(_) for _ in row), file=f)
