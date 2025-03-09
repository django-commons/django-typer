#compdef {{ manage_script_name }}

{{ complete_func }}() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    
    # Extract --settings and --pythonpath options and their values if present because
    # we need to pass these to the complete script - they may be necessary to find the command!
    local settings_option=""
    local pythonpath_option=""
    local manage="{% if is_installed %}{{ manage_script_name }}{% endif %}"
    {% if not is_installed %}
    if [[ ${words[2]} == *{{manage_script_name}} ]]; then
        manage="${words[1]} ${words[2]}"
    else
        manage="${words[1]}"
    fi
    {% endif %}

    for ((i=1; i<$CURRENT; i++)); do
      case "${words[i]}" in
        --settings|--settings=*)
        # Only pass settings to completion script if we're sure it's value does not itself need completion!
        if [[ "${words[i]}" == --settings=* ]]; then
          settings_option="${words[i]}"
        elif (( i + 1 < CURRENT )) && [[ -n "${words[i+1]}" ]] && [[ "${words[i+1]}" != --* ]]; then
          settings_option="--settings=${words[i+1]}"
        fi
        ;;
        --pythonpath|--pythonpath=*)
        # Only pass pythonpath to completion script if we're sure it's value does not itself need completion!
        if [[ "${words[i]}" == --pythonpath=* ]]; then
          pythonpath_option="${words[i]}"
        elif (( i + 1 < CURRENT )) && [[ -n "${words[i+1]}" ]] && [[ "${words[i+1]}" != --* ]]; then
          pythonpath_option="--pythonpath=${words[i+1]}"
        fi
        ;;
      esac
    done

    response=("${(@f)$("${manage}" {{ django_command }} --shell zsh ${settings_option:+${settings_option}} ${pythonpath_option:+${pythonpath_option}} {{ color }} complete {{ fallback }} "${words[*]}" "$CURSOR")}")

    for type key descr in ${response}; do
        if [[ "$type" == "dir" ]]; then
            _path_files -/
        elif [[ "$type" == "file" ]]; then
            _path_files -f
        else
            if [[ "$descr" == "_" ]]; then
                completions+=("$key")
            else
                completions_with_descriptions+=("$key":"$descr")
            fi
        fi
    done

    if [ -n "$completions_with_descriptions" ]; then
        _describe -V unsorted completions_with_descriptions
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
