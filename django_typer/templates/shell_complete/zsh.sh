#compdef {{ manage_script_name }}

{{ complete_func }}() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    
    # Extract --settings and --pythonpath options and their values if present because
    # we need to pass these to the complete script - they may be necessary to find the command!
    local settings_option=""
    local pythonpath_option=""

    {% if is_installed %}
    (( ! $+commands[%(prog_name)s] )) && return 1
    {% endif %}

    for ((i=1; i<$CURRENT; i++)); do
      case "${words[i]}" in
        --settings)
        # Only pass settings to completion script if we're sure it's value does not itself need completion!
        if (( i + 1 < CURRENT )) && [[ -n "${words[i+1]}" ]] && [[ "${words[i+1]}" != --* ]]; then
          settings_option="--settings=${words[i+1]}"
        fi
        ;;
      --pythonpath)
        # Only pass pythonpath to completion script if we're sure it's value does not itself need completion!
        if (( i + 1 < CURRENT )) && [[ -n "${words[i+1]}" ]] && [[ "${words[i+1]}" != --* ]]; then
          pythonpath_option="--pythonpath=${words[i+1]}"
        fi
        ;;
      esac
    done

    {% if not is_installed %}
    if [[ ${words[2]} == *{{manage_script_name}} ]]; then
        cmd="${words[1]} ${words[2]}"
    else
        cmd="${words[1]}"
    fi
    {% else %}
    cmd = "{{ manage_script_name }}"
    {% endif %}

    response=("${(@f)$("${cmd}" {{ django_command }} --shell zsh ${settings_option:+${settings_option}} ${pythonpath_option:+${pythonpath_option}} {{ color }} complete "${words[*]}")}")

    for type key descr in ${response}; do
        if [[ "$type" == "plain" ]]; then
            if [[ "$descr" == "_" ]]; then
                completions+=("$key")
            else
                completions_with_descriptions+=("$key":"$descr")
            fi
        elif [[ "$type" == "dir" ]]; then
            _path_files -/
        elif [[ "$type" == "file" ]]; then
            _path_files -f
        fi
    done

    if [ -n "$completions_with_descriptions" ]; then
        _describe -V unsorted completions_with_descriptions -U
    fi

    if [ -n "$completions" ]; then
        compadd -U -V unsorted -a completions
    fi
}

if [[ $zsh_eval_context[-1] == loadautofunc ]]; then
    # autoload from fpath, call function directly
    {{ complete_func }} "$@"
else
  compdef {{ complete_func }} {{ manage_script_name }}
fi
