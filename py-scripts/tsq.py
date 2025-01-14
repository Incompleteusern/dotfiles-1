#########
## TSQ ##
#########

# See https://github.com/cjquines/tsqx for a better version
# Also see https://github.com/vEnhance/dotfiles/blob/main/vim/after/syntax/tsq.vim for a syntax highlighter

import argparse
import string
import sys

fn_names = {
    "circumcenter": 3,
    "orthocenter": 3,
    "incircle": 3,
    "circumcircle": 3,
    "centroid": 3,
    "incenter": 3,
    "midpoint": 1,
    "extension": 4,
    "foot": 3,
    "CP": 2,
    "CR": 2,
    "dir": 1,
    "conj": 1,
    "intersect": 2,
    "IP": 2,
    "OP": 2,
    "Line": 2,
    "bisectorpoint": 2,
    "arc": 4,
    "abs": 1,
}
short_names = {
    "circle": "circumcircle",
    "rightangle": "rightanglemark",
}
# The following is really bad
for letter in string.ascii_uppercase:
    fn_names["-%s+2*foot" % letter] = 3
    fn_names["-%sp+2*foot" % letter] = 3
    fn_names["-%ss+2*foot" % letter] = 3
    for digit in "0123456789":
        fn_names["-%s_%s+2*foot" % (letter, digit)] = 3


def autoParen(tokens):
    if len(tokens) == 0:
        return ""
    else:
        t = tokens.pop(0)

    if t in short_names:
        t = short_names[t]
    if t in fn_names:
        nargs = fn_names[t]
        args = [autoParen(tokens) for i in range(nargs)]
        return t + "(" + ", ".join(args) + ")"
    else:
        return t


# argument parsing
parser = argparse.ArgumentParser(description="Generate a diagram.")
parser.add_argument(
    "-p",
    "--pre",
    help="Adds an Asymptote preamble.",
    action="store_true",
    dest="preamble",
    default=False,
)
parser.add_argument(
    "-t",
    "--terse",
    help="Omits the source code at the end",
    action="store_true",
    dest="terse",
    default=False,
)
parser.add_argument(
    "-n",
    "--no-trans",
    help="Temporarily disables the transparencies.",
    action="store_true",
    dest="notrans",
    default=False,
)
parser.add_argument(
    "fname",
    help="If provided, reads from the designated file rather than stdin",
    metavar="filename",
    nargs="?",
    default="",
)
parser.add_argument(
    "-s",
    "--size",
    help="If provided, sets the image size in the preamble. (Use with -p.)",
    action="store",
    dest="size",
    default="8cm",
)
parser.add_argument(
    "-f",
    "--fontsize",
    help="If provided, sets the image size in the preamble. (Use with -p.)",
    action="store",
    dest="fontsize",
    default="9pt",
)
opts = parser.parse_args()

# Initialize some stuff
raw_code = ""
dot_code = ""

GENERIC_PREAMBLE = r"""
usepackage("amsmath");
usepackage("amssymb");
settings.tex="pdflatex";
settings.outformat="pdf";
// Replacement for olympiad+cse5 which is not standard
import geometry;
// recalibrate fill and filldraw for conics
void filldraw(picture pic = currentpicture, conic g, pen fillpen=defaultpen, pen drawpen=defaultpen)
    { filldraw(pic, (path) g, fillpen, drawpen); }
void fill(picture pic = currentpicture, conic g, pen p=defaultpen)
    { filldraw(pic, (path) g, p); }
// some geometry
pair foot(pair P, pair A, pair B) { return foot(triangle(A,B,P).VC); }
pair orthocenter(pair A, pair B, pair C) { return orthocentercenter(A,B,C); }
pair centroid(pair A, pair B, pair C) { return (A+B+C)/3; }
// cse5 abbreviations
path CP(pair P, pair A) { return circle(P, abs(A-P)); }
path CR(pair P, real r) { return circle(P, r); }
pair IP(path p, path q) { return intersectionpoints(p,q)[0]; }
pair OP(path p, path q) { return intersectionpoints(p,q)[1]; }
path Line(pair A, pair B, real a=0.6, real b=a) { return (a*(A-B)+A)--(b*(B-A)+B); }
""".strip()

if opts.preamble:
    print("defaultpen(fontsize(%s));" % opts.fontsize)
    print("size(%s);" % opts.size)
    print(GENERIC_PREAMBLE)
if opts.fname != "":
    stream = open(opts.fname, "r")
else:
    stream = sys.stdin  # type: ignore

in_comment_mode = False
# Print output
for line in stream:
    line = line.strip()

    # Empty line = newspace
    if line == "":
        print("")
        raw_code += line + "\n"
        continue

    # Handling of comments
    if line[:2] == "//":
        print(line)
        raw_code += line + "\n"
        continue
    if line[:2] == "/*" and line.endswith("*/"):
        print(line)
        continue
    elif line[:2] == "/*":
        in_comment_mode = True
        print(line)
        continue
    elif in_comment_mode and line.endswith("*/"):
        in_comment_mode = False
        print("*/")
        continue
    if in_comment_mode:
        print(line)
        continue

    raw_code += line + "\n"

    # Verbatim
    if line[0] == "!":
        print(line[1:].strip())
        continue

    # Decide whether to auto-paren
    if line[0] == ".":
        # Force auto paren
        do_auto_paren = True
        line = line[1:].strip()
    elif line[0] == ">":
        do_auto_paren = False
        line = line[1:].strip()
    else:
        do_auto_paren = not (", " in line)  # just default to auto-ing unless , appears

    if "=" in line:
        raw_name, raw_expr = line.split("=", 2)
        if len(raw_name) > 0 and raw_name[-1] == ":":
            draw_point = False
            label_point = False
            raw_name = raw_name[:-1].strip()
        elif len(raw_name) > 0 and raw_name[-1] == ".":
            draw_point = True
            label_point = False
            raw_name = raw_name[:-1].strip()
        else:
            draw_point = True
            label_point = True
        raw_name = raw_name.strip()
        point_name = (
            raw_name.replace("'", "p").replace("*", "s").replace("^", "")
        )  # name used in source code
        label_name = raw_name.replace(
            "*", r"^\ast"
        )  # name passed to LaTeX label function

        if do_auto_paren:
            tokens = raw_expr.strip().split(" ")
            expr = autoParen(tokens)
            if len(tokens) == 0:
                direction = "dir(" + point_name + ")"
            elif len(tokens) == 1:
                magnitude, angle = tokens[0].split("R", 2)
                direction = "dir(" + angle + ")"
                if magnitude != "":
                    direction = magnitude + "*" + direction
            else:
                raise ValueError(f"Too many tokens in {tokens}")
        else:
            expr = raw_expr.strip()
            direction = "dir(" + point_name + ")"

        if point_name != "":
            print("pair %s = %s;" % (point_name, expr))
        if draw_point:
            if label_point:
                dot_code += 'dot("$%s$", %s, %s);\n' % (
                    label_name,
                    point_name,
                    direction,
                )
            else:
                dot_code += "dot(%s);\n" % (point_name if point_name else expr)

    else:
        line = line.strip()
        pen = None
        if do_auto_paren:
            tokens = line.split(" ")
            expr = autoParen(tokens)
            # 0.2 mediumcyan / blue -> opacity(0.2)+mediumcyan, blue
            if "/" in tokens:
                tindex = tokens.index("/")  # index of transparency divider
                if tokens[0][0] == "0":  # first token is leading 0
                    fillpen = "opacity(" + tokens[0] + ")"
                    if tindex != 1:
                        fillpen += "+" + "+".join(tokens[1:tindex])  # add on others
                else:
                    fillpen = "+".join(tokens[0:tindex])
                drawpen = "+".join(tokens[tindex + 1 :])
                if not drawpen:
                    drawpen = "defaultpen"

                if opts.notrans:
                    print("draw(" + expr + ", " + drawpen + ");")
                else:
                    print("filldraw(" + expr + ", " + fillpen + ", " + drawpen + ");")
            else:
                pen = "+".join(tokens)  # any remaining tokens
        else:
            expr = line  # you'll have to put commas here for pens manually
            pen = ""

        if pen:
            print("draw(" + expr + ", " + pen + ");")
        elif pen is not None:
            print("draw(" + expr + ");")

print("\n" + dot_code)
if opts.terse:
    print("/* Source generated by TSQ */")
else:
    print("/* TSQ Source:")
    print("")
    print(raw_code.strip())
    print("")
    print("*/")

stream.close()
