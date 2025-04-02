Import-Module PSReadLine
Set-PSReadLineKeyHandler -Chord Tab -Function MenuComplete
$scriptblock = {
    param($wordToComplete, $commandAst, $cursorPosition)
    
    $commandText = $commandAst.Extent.Text

    # trailing white space is lopped off, add it back if necessary
    if ($cursorPosition -gt $commandText.Length) {
        $commandText += " "
    }

    $settingsOption = ""
    if ($commandText -match "--settings(?:\s+|=)([^\s]+)\s+") {
        $settingsOption = "--settings=$($matches[1])"
    }

    $pythonPathOption = ""
    if ($commandText -match "--pythonpath(?:\s+|=)([^\s]+)\s+") {
        $pythonPathOption = "--pythonpath=$($matches[1])"
    }

    $arguments = @("{{ django_command }}") +
    @($settingsOption) +
    @($pythonPathOption) +
    @("--shell", "pwsh", "complete", "{{ fallback }}", $commandText, $cursorPosition) |
    Where-Object { $_ }

    $results = & {{ manage_script_name }} @arguments 2>&1

    if ($results.Count -eq 0) {
        # avoid default path completion
        return $null
    }

    $results | ForEach-Object {
        $commandArray = $_ -Split ":::"
        $type = $commandArray[0]
        $value = $commandArray[1]
        $help = $commandArray[2]
        if ($help -eq "") {
            [System.Management.Automation.CompletionResult]::new($value)
        } else {
            [System.Management.Automation.CompletionResult]::new($value, $value, 'ParameterValue', $help)
        }
    }
}
Register-ArgumentCompleter -Native -CommandName {{ manage_script_name }} -ScriptBlock $scriptblock
