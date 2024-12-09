{% if is_installed %}
#compdef {{ manage_script }}
{% else %}
#compdef {{ manage_script.absolute }} {{ manage_script.name }} ./{{ manage_script.name }} */{{ manage_script.name }}
{% endif %}

{% if is_installed %}
{% endif %}

{{ complete_func }}() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    
    # Extract --settings and --pythonpath options and their values if present becase
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

    response=("${(@f)$({% if is_installed %}{{ manage_script }}{% else %}{{ python }} {{ manage_script.absolute }}{% endif %} {{ django_command }} --shell zsh ${settings_option:+${settings_option}} ${pythonpath_option:+${pythonpath_option}} {{ color }} {{ rich }} complete "${words[*]}")}")

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
    # eval/source/. command, register function for later
    compdef {{ complete_func }} {% if is_installed %}{{ manage_script }}{% else %}'*{{ manage_script.name }}'{% endif %}
fi
