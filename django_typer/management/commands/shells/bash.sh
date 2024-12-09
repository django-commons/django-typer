%(complete_func)s() {
    local IFS=$'
'
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

    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   %(autocomplete_var)s=complete_bash $1 {{ django_command }} --shell bash ${settings_option:+${settings_option}} ${pythonpath_option:+${pythonpath_option}} {{ color }} complete ) )
    return 0
}

complete -o default -F %(complete_func)s %(prog_name)s
