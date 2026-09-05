# Opens the small GitHub PR that adds test_sentences/lt.txt to rhasspy/piper-samples
# (the catalogue's sample generator needs it; 82 files there, lt missing - measured 09-05).
#
#   powershell -File piper_samples_pr.ps1            # dry run: fork + branch + commit, NO push
#   powershell -File piper_samples_pr.ps1 -Run       # push + PR
#   powershell -File piper_samples_pr.ps1 -Run -VoicesPr 103   # mentions the piper-voices PR number
param([switch]$Run, [string]$VoicesPr = "")
$ErrorActionPreference = "Stop"
$cia   = Split-Path -Parent $MyInvocation.MyCommand.Path
$work  = "D:\_Balsas Lietuviksas\_darbal\piper_samples_pr"
$saka  = "lt-test-sentences"
$src   = Join-Path $cia "lt.txt"
if (-not (Test-Path $src)) { throw "nėra $src" }

if (-not (Test-Path $work)) {
    gh repo fork rhasspy/piper-samples --clone=false 2>&1 | Out-Host
    git clone --depth 1 https://github.com/RobertasTa/piper-samples $work | Out-Host
}
Set-Location $work
if (-not (git remote | Select-String -Quiet "^upstream$")) { git remote add upstream https://github.com/rhasspy/piper-samples }
git fetch upstream master | Out-Host
git checkout -B $saka upstream/master | Out-Host
Copy-Item $src (Join-Path $work "test_sentences\lt.txt") -Force
git add test_sentences/lt.txt
$msg = @'
Add Lithuanian test sentences (lt.txt)

First sentences of the Lithuanian Wikipedia article on the rainbow, matching
lv.txt and et.txt, so generate-samples.sh can produce samples for the
lt_LT-reginute1-medium voice.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
'@
git commit -m $msg | Out-Host
git --no-pager show --stat HEAD | Out-Host

if (-not $Run) { Write-Host "`nDRY RUN - nepush'inta, PR nesukurtas. Šaka $saka paruošta $work"; exit 0 }

git push -u origin $saka --force | Out-Host
$nuoroda = if ($VoicesPr) { "the Lithuanian voice submitted in rhasspy/piper-voices PR #$VoicesPr" } else { "the Lithuanian voice lt_LT-reginute1-medium submitted to rhasspy/piper-voices" }
$body = @"
Adds ``test_sentences/lt.txt`` (Lithuanian): the first sentences of the Lithuanian Wikipedia article on the rainbow, the same source as ``lv.txt`` and ``et.txt``.

Needed by ``_script/generate-samples.sh`` for $nuoroda. Note that this voice uses ``phoneme_type: text`` with its own phonemizer, so regenerating its sample needs the module shipped with the voice; the shipped ``samples/speaker_0.mp3`` was made from the first line of this file.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
"@
gh pr create --repo rhasspy/piper-samples --base master --head "RobertasTa:$saka" --title "Add Lithuanian test sentences (lt.txt)" --body $body | Out-Host
