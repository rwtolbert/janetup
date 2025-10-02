# This file must be used with "source <venv>/bin/activate.fish" *from fish*
# (https://fishshell.com/); you cannot run it directly.

function deactivate -d "Exit Janet environment and return to normal shell environment"
    # reset old environment variables
    if test -n "$_OLD_PATH"
        set -gx PATH $_OLD_PATH
    end
    set -e _OLD_PATH

    if test -n "$_OLD_JANET_PATH"
        set -gx JANET_PATH $_OLD_JANET_PATH
    end
    set -e _OLD_JANET_PATH

    if test -n "$_OLD_FISH_PROMPT_OVERRIDE"
        functions -e fish_prompt
        functions -c _old_fish_prompt fish_prompt
        functions -e _old_fish_prompt
    end
    set -e _OLD_FISH_PROMPT_OVERRIDE

    set -e JANET_VIRTUAL_ENV
    if test "$argv[1]" != "nondestructive"
        # Self-destruct!
        functions -e deactivate
    end
end

# Unset irrelevant variables.
deactivate nondestructive

# don't use JANET_PATH in here
# store an old one from outside, but don't set a new
# one
set -gx _OLD_JANET_PATH "$JANET_PATH";
set -e JANET_PATH

set -gx _OLD_PATH "$PATH";

set -gx JANET_VIRTUAL_ENV "{venv_name}"
set -gx PATH "{venv_dir}"/bin "{venv_dir}"/lib/janet/bin $PATH

if test -z "$VIRTUAL_ENV_DISABLE_PROMPT"
    # fish uses a function instead of an env var to generate the prompt.

    # Save the current fish_prompt function as the function _old_fish_prompt.
    functions -c fish_prompt _old_fish_prompt

    # With the original prompt function renamed, we can override with our own.
    function fish_prompt
        # Save the return status of the last command.
        set -l old_status $status

        # Output the venv prompt; color taken from the blue from the Janet home page
        printf "%s%s%s" (set_color 076D96) "($JANET_VIRTUAL_ENV) " (set_color normal)

        # Restore the return status of the previous command.
        echo "exit $old_status" | .
        # Output the original/"old" prompt.
        _old_fish_prompt
    end

    set -gx _OLD_FISH_PROMPT_OVERRIDE "$JANET_VIRTUAL_ENV"
end
