#!/bin/zsh

export LANG="en_US.UTF-8"
export LC_ALL=""
export EDITOR=vim
export PGCLIENTENCODING="utf8"
export PATH="/home/niwi/bin:$PATH"

export WORKON_HOME=~/.virtualenvs
export VIRTUALENVWRAPPER_PYTHON="/usr/bin/python2.7"
source /usr/bin/virtualenvwrapper.sh

bindkey    "^[[3~"          delete-char
bindkey    "^[3;5~"         delete-char
bindkey    '^R'             history-incremental-search-backward

autoload -U promptinit
promptinit
prompt zefram


#------------------------------
## Comp stuff
##------------------------------
zmodload zsh/complist 
autoload -Uz compinit
compinit
zstyle :compinstall filename '${HOME}/.zshrc'

zstyle ':completion:*:pacman:*' force-list always
zstyle ':completion:*:*:pacman:*' menu yes select
zstyle ':completion:*:default' list-colors ${(s.:.)LS_COLORS}
zstyle ':completion:*:*:kill:*' menu yes select
zstyle ':completion:*:kill:*'   force-list always
zstyle ':completion:*:*:killall:*' menu yes select
zstyle ':completion:*:killall:*'   force-list always


#------------------------------
# Alias stuff
#------------------------------
alias ls="ls --color -F"
alias ll="ls --color -lh"
alias 'lsd'='ls -d *(/)'
alias 'lsf'='ls -h *(.)'
alias 'rm'='rm -r'
alias 'cp'='cp -r'
alias 'term'='xterm -bg black -fg white'
alias 'pdf'='evince'
alias 'l'='ls --color -GFlh'


#-----------------
# Options
#-----------------

setopt AUTO_CD               # implicate cd for non-commands
#setopt CD_ABLE_VARS       # read vars in cd
setopt CORRECT_ALL            # correct spelling
setopt COMPLETE_IN_WORD    # complete commands anywhere in the word
setopt NOTIFY              # Notify when jobs finish
#setopt C_BASES             # 0xFF
setopt BASH_AUTO_LIST      # Autolist options on repeition of ambiguous args
#setopt CHASE_LINKS         # Follow links in cds
#setopt AUTO_PUSHD          # Push dirs into history
#setopt ALWAYS_TO_END       # Move to the end on complete completion
#setopt LIST_ROWS_FIRST     # Row orientation for menu
setopt MULTIOS             # Allow Multiple pipes
#setopt MAGIC_EQUAL_SUBST   # Expand inside equals
setopt EXTENDED_GLOB
setopt NOBEEP
setopt INC_APPEND_HISTORY

export HISTSIZE=1000
export SAVEHIST=1000
export HISTFILE=~/.zhistory

## OTHER OPTS
setopt hist_ignore_all_dups
setopt hist_ignore_space


#------------------------------
# Window title
#------------------------------
case $TERM in
    *xterm*|rxvt|rxvt-unicode|rxvt-256color|(dt|k|E)term)
		precmd () { print -Pn "\e]0;$TERM - (%L) [%n@%M]%# [%~]\a" } 
		preexec () { print -Pn "\e]0;$TERM - (%L) [%n@%M]%# [%~] ($1)\a" }
	;;
    screen)
    	precmd () { 
			print -Pn "\e]83;title \"$1\"\a" 
			print -Pn "\e]0;$TERM - (%L) [%n@%M]%# [%~]\a" 
		}
		preexec () { 
			print -Pn "\e]83;title \"$1\"\a" 
			print -Pn "\e]0;$TERM - (%L) [%n@%M]%# [%~] ($1)\a" 
		}
	;; 
esac
