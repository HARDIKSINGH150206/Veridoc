# Development helper for the synthetic audio in issue #12; never run by the app or tests.
# Uses the installed Windows speech engine offline. The committed WAV works on every OS.
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$fixtureSpeech = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $fixtureSpeech.SelectVoice('Microsoft Zira Desktop')
    $fixtureSpeech.Rate = -1
    $fixtureSpeech.Volume = 100
    $fixtureFormat = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(
        16000,
        [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen,
        [System.Speech.AudioFormat.AudioChannel]::Mono
    )
    $fixtureScript = Get-Content -LiteralPath (
        Join-Path $PSScriptRoot 'delivery-22-nov.transcript.txt'
    ) -Encoding UTF8 -Raw
    $fixtureSpeech.SetOutputToWaveFile(
        (Join-Path $PSScriptRoot 'delivery-22-nov.wav'), $fixtureFormat
    )
    $fixtureSpeech.Speak($fixtureScript.Trim())
} finally {
    $fixtureSpeech.Dispose()
}
