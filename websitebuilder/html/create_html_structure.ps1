# Creates the directory structure and placeholder HTML files for this workspace's `html` folder.
# Place this script in the `html` folder and run it in PowerShell.

$root = $PSScriptRoot

$paths = @(
    'Automotive\CarDealership.html',
    'ecommerce\DigitalDownloads.html',
    'ecommerce\electronics.html',
    'ecommerce\Fashionstores.html',
    'ecommerce\GroceryStore.html',
    'ecommerce\Handmadeproducts.html',
    'ecommerce\languagelearning .html',
    'ecommerce\universitiesschools.html',
    'Education\CoachingInstitute.html',
    'Education\educationlearning.html',
    'Entertainment\Music.html',
    'Finance\banking.html',
    'Finance\stocktrading.html',
    'Health\Fitnessgym.html',
    'Health\MedicalClinics.html',
    'Health\Mentalhealth.html',
    'Health\NutritionDiet.html',
    'Health\telemedicineplatforms.html',
    'Hospitality\barsnightclubs.html',
    'Hospitality\cateringservices.html',
    'Hospitality\FoodDeliveryServices.html',
    'Hospitality\Hotelsresorts.html',
    'Hospitality\Restaurantcafes.html',
    'Legal\Digitalnotaryservices.html',
    'Legal\LawFirms.html',
    'Legal\Legalconsultation.html',
    'personalportfolio\projectbased1.html',
    'personalportfolio\projectbased2.html',
    'personalportfolio\projectsbased.html',
    'personalportfolio\webdeveloper.html',
    'personalportfolio\webdeveloper2.html',
    'Realestate\agentportfolio.html',
    'Realestate\Commerciallistings.html',
    'Realestate\luxuryrealestate.html',
    'Realestate\rentalservices.html',
    'Realestate\residentialproperties.html',
    'sports\gymfitnesscentres.html',
    'sports\personaltraining.html',
    'sports\yoga.html',
    'technology\Hosting.html',
    'technology\ITconsultancy.html',
    'technology\saas.html',
    'Travel\adventuretourism.html',
    'Travel\TravelAgencies.html'
)

foreach ($p in $paths) {
    $full = Join-Path $root $p
    $dir = Split-Path $full -Parent
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    if (-not (Test-Path $full)) {
        $title = [System.IO.Path]::GetFileNameWithoutExtension($full)
        $content = @"<!-- Placeholder: $p -->
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>$title</title>
</head>
<body>
  <h1>$title</h1>
  <p>Placeholder file created by create_html_structure.ps1</p>
</body>
</html>
"@
        $content | Out-File -FilePath $full -Encoding UTF8
    }
}

# Generate a simple tree-style listing into structure_tree.txt
$treeFile = Join-Path $root 'structure_tree.txt'
Get-ChildItem -Path $root -Recurse | Sort-Object FullName | ForEach-Object {
    $relative = $_.FullName.Substring($root.Length+1).TrimStart('\')
    if ($_.PSIsContainer) { "[$relative]" } else { "  $relative" }
} | Out-File -FilePath $treeFile -Encoding UTF8

Write-Host "Structure created (or verified). See: $treeFile" -ForegroundColor Green
