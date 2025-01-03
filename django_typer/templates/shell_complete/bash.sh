{{ complete_func }}() {
    local IFS=$'
'
    local response
    # Extract --settings and --pythonpath options and their values if present becase
    # we need to pass these to the complete script - they may be necessary to find the command!
    local settings_option=""
    local pythonpath_option=""
    
    for ((i=0; i<COMP_CWORD; i++)); do
        case "${COMP_WORDS[i]}" in
            --settings)
                # Ensure the next word exists and is not another flag
                if [[ $((i + 1)) -lt $COMP_CWORD ]]; then
                    settings_option="--settings=${COMP_WORDS[i+1]}"
                fi
                ;;
            --pythonpath)
                # Ensure the next word exists and is not another flag
                if [[ $((i + 1)) -lt $COMP_CWORD ]]; then
                    pythonpath_option="--pythonpath=${COMP_WORDS[i+1]}"
                fi
                ;;
        esac
    done

    response=()
    while IFS= read -r line; do
        response+=("$line")
    done < <( $1 {{ django_command }} --shell bash ${settings_option:+${settings_option}} ${pythonpath_option:+${pythonpath_option}} {{ color }} complete "${COMP_WORDS[*]}" )
    
    COMPREPLY=()
    for completion in "${response[@]}"; do
        IFS=',' read type value <<< "$completion"

        if [[ $type == 'dir' ]]; then
            COMPREPLY=()
            compopt -o dirnames
        elif [[ $type == 'file' ]]; then
            COMPREPLY=()
            compopt -o default
        else
            COMPREPLY+=($value)
        fi
    done

    return 0
}

{{ complete_func }}_setup() {
    complete {{ complete_opts }} -F {{ complete_func }} {{ manage_script_name }}
}

{{ complete_func }}_setup;
