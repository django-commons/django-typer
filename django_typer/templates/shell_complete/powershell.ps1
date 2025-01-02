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

    {{ manage_script_name }} {{ django_command }} $settingsOption $pythonPathOption --shell {{ shell }} {{ color }} complete "$($commandText)" | ForEach-Object {
        $commandArray = $_ -Split ":::"
        $command = $commandArray[0]
        $helpString = $commandArray[1]
        [System.Management.Automation.CompletionResult]::new(
            $command, $command, 'ParameterValue', $helpString)
    }
}
Register-ArgumentCompleter -Native -CommandName {{ manage_script_name }} -ScriptBlock $scriptblock
