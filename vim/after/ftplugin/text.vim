" tsq -> asy compile and open
nnoremap <localleader>p :update<CR>:silent !python -m tsq -p % \| asy -f pdf -V - &<CR>:redraw<CR>
" tsq -> asy
nnoremap <localleader>a :update<CR>:!python -m tsq -p % \| asy -f pdf -<CR><CR>:redraw<CR>
" tsq -> asy but show error
nnoremap <localleader>o :update<CR>:!python -m tsq -p % \| asy -f pdf -<CR>

let b:ale_linters = ['proselint', 'languagetool']
