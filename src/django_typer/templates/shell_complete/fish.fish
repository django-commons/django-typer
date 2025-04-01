function __fish_{{prog_name}}_complete

    set cmd (commandline)
    set cursor (commandline -C)

    set completeCmd {{ django_command }} --shell fish {{ color }} complete  {{ fallback }} "$cmd" "$cursor"

    # We'll extract --settings=... and --pythonpath=... if present
    set settingsOption ''
    set pythonPathOption ''

    set match (string match -r -- '--settings(?:[ =])([^ ]+)' $cmd)
    if [ (count $match) -gt 0 ]
        set settingsVal (string replace -r -- '.*--settings(?:[ =])([^ ]+).*' '$1' $cmd)
        set settingsOption "--settings=$settingsVal"
    end

    set match (string match -r -- '--pythonpath(?:[ =])([^ ]+)' $cmd)
    if [ (count $match) -gt 0 ]
        set pythonPathVal (string replace -r -- '.*--pythonpath(?:[ =])([^ ]+).*' '$1' $cmd)
        set pythonPathOption "--pythonpath=$pythonPathVal"
    end

    # Only add these options if they're non-empty
    if test -n "$settingsOption"
        set completeCmd $completeCmd $settingsOption
    end
    if test -n "$pythonPathOption"
        set completeCmd $completeCmd $pythonPathOption
    end

    set results ({{ manage_script_name }} $completeCmd)

    for completion in $results;
        set -l metadata (string split "," $completion);

        if test $metadata[1] = "dir";
            __fish_complete_directories $metadata[2];
        else if test $metadata[1] = "file";
            __fish_complete_path $metadata[2];
        else
            echo $metadata[2];
        end;
    end;
end

complete -c {{ manage_script_name }} --no-files --arguments '(__fish_{{prog_name}}_complete)'
