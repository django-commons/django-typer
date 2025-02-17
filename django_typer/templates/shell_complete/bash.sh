{{ complete_func }}() {
    local IFS=$'
'
    local response
    # Extract --settings and --pythonpath options and their values if present becase
    # we need to pass these to the complete script - they may be necessary to find the command!
    local settings_option=""
    local pythonpath_option=""

    COMP_WORDBREAKS="${COMP_WORDBREAKS//=/}"
    
    for ((i=0; i<COMP_CWORD; i++)); do
        case "${COMP_WORDS[i]}" in
            --settings|--settings=*)
                # Ensure the next word exists and is not another flag
                if [[ "${COMP_WORDS[i]}" == --settings=* ]]; then
                    settings_option="${COMP_WORDS[i]}"
                elif [[ $((i + 1)) -lt $COMP_CWORD ]]; then
                    settings_option="--settings=${COMP_WORDS[i+1]}"
                fi
                ;;
            --pythonpath|--pythonpath=*)
                # Ensure the next word exists and is not another flag
                if [[ "${COMP_WORDS[i]}" == --pythonpath=* ]]; then
                    pythonpath_option="${COMP_WORDS[i]}"
                elif [[ $((i + 1)) -lt $COMP_CWORD ]]; then
                    pythonpath_option="--pythonpath=${COMP_WORDS[i+1]}"
                fi
                ;;
        esac
    done

    response=()
    while IFS= read -r line; do
        response+=("$line")
    done < <( $1 {{ django_command }} --shell bash ${settings_option:+${settings_option}} ${pythonpath_option:+${pythonpath_option}} {{ color }} complete {{ fallback }} "${COMP_WORDS[*]}" "$COMP_POINT" )
    
    COMPREPLY=()
    set_mode=true
    for completion in "${response[@]}"; do
        IFS=',' read type value <<< "$completion"

        {% if use_compopt %}
        if $set_mode; then
            if [[ $type == 'dir' ]]; then
                compopt -o dirnames
            elif [[ $type == 'file' ]]; then
                compopt -o default
                set_mode=false
            fi
        fi
        {% endif %}
        COMPREPLY+=($value)
    done

    return 0
}

{{ complete_func }}_setup() {
    complete {{ complete_opts }} -F {{ complete_func }} {{ manage_script_name }}
}

{{ complete_func }}_setup;
