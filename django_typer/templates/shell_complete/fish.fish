function __fish_{{prog_name}}_complete
    # Get the entire current command line
    set cmd (commandline)

    # Position of the cursor (for detecting trailing whitespace)
    set cursor (commandline -C)

    # If the cursor extends beyond the length of the text, there's trailing space
    if test $cursor -gt (string length $cmd)
        set cmd "$cmd "
    end

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

    set results ({{ manage_script_name }} {{ django_command }} $settingsOption $pythonPathOption --shell fish {{ color }} complete "$cmd")

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

complete -c {{ manage_script_name }} -no-files --arguments '(__fish_manage_complete)'
