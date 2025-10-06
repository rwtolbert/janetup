# . bin/load_janet

# check for existing
if [[ -v JANET_CURRENT_ENV && -n $JANET_CURRENT_ENV ]] ; then
    echo "There is already a Janet env active, please run 'unload_janet' first."
    return
fi

# store a JANET_PATH if it exists before
if [[ -v JANET_PATH && -n $JANET_PATH ]] ; then
    _OLD_JANET_PATH="$JANET_PATH";
    export _OLD_JANET_PATH;
fi

# store a JANET_PREFIX if it exists before
if [[ -v JANET_PREFIX && -n $JANET_PREFIX ]] ; then
    _OLD_JANET_PREFIX="$JANET_PREFIX";
    export _OLD_JANET_PREFIX;
fi

# store a JANET_BUILD_TYPE if it exists before
if [[ -v JANET_BUILD_TYPE && -n $JANET_BUILD_TYPE ]] ; then
    _OLD_JANET_BUILD_TYPE="$JANET_BUILD_TYPE";
    export _OLD_JANET_BUILD_TYPE;
fi

_OLD_PATH="$PATH";
_OLD_PS1="$PS1";
JPATH="{venv_dir}";
PATH="$JPATH"/bin:"$JPATH"/lib/janet/bin:"$PATH";
JANET_BUILD_TYPE="{build_type}"
JANET_CURRENT_ENV="{venv_name}"
PS1="("{venv_name}") ${{PS1:-}}"
export _OLD_PATH;
export _OLD_PS1;
export PATH;
export PS1;
export JANET_BUILD_TYPE;
export JANET_CURRENT_ENV;

# don't use JANET_PATH inside here
unset JANET_PATH;
export JANET_PATH;
unset JANET_PREFIX;
export JANET_PREFIX;

unload_janet() {{
  PATH="$_OLD_PATH";

  unset JANET_PATH
  if [[ -v _OLD_JANET_PATH && -n $_OLD_JANET_PATH ]] ; then
      JANET_PATH="$_OLD_JANET_PATH";
  fi
  export JANET_PATH;

  unset JANET_PREFIX
  if [[ -v _OLD_JANET_PREFIX && -n $_OLD_JANET_PREFIX ]] ; then
      JANET_PREFIX="$_OLD_JANET_PREFIX";
  fi
  export JANET_PREFIX;

  unset JANET_BUILD_TYPE
  if [[ -v _OLD_JANET_BUILD_TYPE && -n $_OLD_JANET_BUILD_TYPE ]] ; then
      JANET_BUILD_TYPE="$_OLD_JANET_BUILD_TYPE";
      export JANET_BUILD_TYPE;
  fi
  export JANET_BUILD_TYPE

  unset JANET_CURRENT_ENV;
  export JANET_CURRENT_ENV;

  PS1="$_OLD_PS1";
  export PATH;
  export PS1;
  unset _OLD_JANET_PATH;
  unset _OLD_JANET_BUILD_TYPE;
  unset _OLD_PATH;
  unset _OLD_PS1;
  unset -f unload_janet;
  export _OLD_JANET_PATH;
  export _OLD_JANET_BUILD_TYPE;
  export _OLD_PATH;
  export _OLD_PS1;
  hash -r 2> /dev/null;
}}
hash -r 2> /dev/null;