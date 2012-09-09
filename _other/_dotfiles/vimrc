call pathogen#infect()

set number
set nocompatible

set bs=2
set ts=4
set tw=1000000000

set expandtab
set tabstop=8
set softtabstop=4
set shiftwidth=4
filetype indent off
filetype plugin on

syntax on

set autoindent
set showmatch
set showmode
set mousehide

set nowrapscan
set hlsearch
set incsearch

set fileencoding=utf8
set encoding=utf8

highlight ExtraWhitespace ctermbg=red guibg=red
au InsertLeave,BufWinEnter * match ExtraWhitespace /\s\+$/

"au ColorScheme * highlight ExtraWhitespace ctermbg=red guibg=red
"au BufRead,BufNewFile * colorscheme desert
"colorscheme desert

" Python snippets
au BufRead,BufNewFile *.py,*pyw set textwidth=140
au BufNewFile *.py 0r ~/.vim/skeleton/python.py
au BufWritePre *.py,*.js,*.html :%s/\s\+$//e


" Line wrapping (?)
"set wrap
"set linebreak
" note trailing space at end of next line
"set showbreak=>\ \ \


" File type settings
au BufRead,BufNewFile *.json set filetype=javascript
au BufRead,BufNewFile *.gsp set filetype=html
au BufRead,BufNewFile *.jinja set filetype=htmldjango

" Command maps
map <F4> :!pep8 %<Cr>


"set mouse=a
if has('gui_running')
  map <S-Insert> <MiddleMouse>
  map! <S-Insert> <MiddleMouse>
endif
