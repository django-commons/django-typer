function __fish_{{prog_name}}_complete

    set cmd (commandline)
    set cursor (commandline -C)

    # We'll extract --settings=... and --pythonpath=... if present so they can
    # be forwarded to the shellcompletion command -- they may be necessary to
    # find the command's INSTALLED_APPS, sys.path entries, etc.
    set settingsOption
    set pythonPathOption

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

    # NB: --settings and --pythonpath are options of the shellcompletion
    # command itself, NOT of its `complete` subcommand. They must appear
    # BEFORE `complete` on the command line.
    set completeCmd {{ django_command }} --shell fish $settingsOption $pythonPathOption {{ color }} complete {{ fallback }} "$cmd" "$cursor"

    set results (env TYPER_USE_RICH=0 {{ manage_script_name }} $completeCmd)

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
