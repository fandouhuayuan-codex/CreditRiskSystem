$features = [ordered]@{
    ID         = 99999
    LIMIT_BAL  = 20000
    SEX        = 1
    EDUCATION  = 2
    MARRIAGE   = 2
    AGE        = 30
    PAY_0      = 8
    PAY_2      = 8
    PAY_3      = 6
    PAY_4      = 6
    PAY_5      = 6
    PAY_6      = 6
    BILL_AMT1  = 20000
    BILL_AMT2  = 19000
    BILL_AMT3  = 18000
    BILL_AMT4  = 17000
    BILL_AMT5  = 16000
    BILL_AMT6  = 15000
    PAY_AMT1   = 0
    PAY_AMT2   = 0
    PAY_AMT3   = 0
    PAY_AMT4   = 0
    PAY_AMT5   = 0
    PAY_AMT6   = 0
}

$body = @{
    features   = $features
    model_name = 'XGBoost'
    threshold  = 0.5
} | ConvertTo-Json -Depth 5

$resp = Invoke-RestMethod -Uri "http://localhost:8000/api/predict/" -Method Post -Body $body -ContentType "application/json; charset=utf-8"
Write-Output "=== 预测结果 ==="
$resp | ConvertTo-Json -Depth 5

Write-Output ""
Write-Output "=== 最新告警列表 ==="
$alerts = Invoke-RestMethod -Uri "http://localhost:8000/api/alerts/?page=1&page_size=3" -Method Get
$alerts | ConvertTo-Json -Depth 5
