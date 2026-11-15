# Báo cáo nhóm — Day 06 · Data Governance & Privacy

## 00 · Thông tin và kết luận

| Mục | Nội dung |
|---|---|
| Nhóm | G02 |
| Đề tài | T02 · Raw QC Triage — ưu tiên ảnh mờ, lóa, tối và lỗi nén để kiểm tra |
| Người phụ trách | Lê Tuấn Khôi (group lead) |
| Mã học viên trong tên repository | 2A202603024 |
| Repository | https://github.com/rifujin123/K5-Day6-L2-LeTuanKhoi-2A202603024-DataGovernanceAndPrivacy |
| Mã nguồn được kiểm tra | Snapshot chạy tại `8c76625`; báo cáo ghép với cập nhật remote `ccd3f45`. SHA trong bằng chứng giữ nguyên theo lượt chạy gốc |
| Ngày đối soát | 14/11/2026 (UTC+7) |
| Quy mô phân công | 7 vai trò; bằng chứng đóng góp được ghi riêng tại mục 10 |
| Tag `demo-180m`, `final-24h` | Chưa có trong Git tại thời điểm kiểm tra |
| Hạn nộp | Không có thông tin xác nhận trong repository |

**Kết quả:** baseline Laplacian và PoC đa đặc trưng đều chạy thành công offline, xếp hạng đủ 96 ảnh và tạo queue 20 ảnh thuộc split eval. Kiểm tra 14 manifest đạt; bộ kiểm thử có **75 passed, 39 skipped, 0 failed, 0 errors**. Preflight có **0 FAIL, 2 WARN** do thiếu các gói dữ liệu/model tùy chọn.

**Giới hạn kết luận:** chưa có ground truth (GT) của giảng viên và chưa có quyết định review thực tế. Vì vậy, chưa có Defect Recall@20, Precision@20 hay bằng chứng PoC tốt hơn baseline về chất lượng. Trạng thái quyết định của queue là **HOLD / REVIEW_PENDING**, với 20/20 mục chưa giải quyết. Pipeline đã vận hành được; đánh giá chất lượng và phê duyệt của con người còn chờ bằng chứng.

Các số liệu dưới đây được đối soát với [kết quả tổng hợp](results_summary.json), [so sánh vận hành](operational_comparison.md), [phân tích thứ hạng](ranking_diagnostics.csv) và [log kiểm thử](evidence/pytest_report.txt).

## 01 · Bài toán và phạm vi

T02 đặt budget cố định B=20: từ tập ảnh đầu vào, hệ thống xếp các ảnh nghi lỗi lên trước để QC tập trung kiểm tra. Bỏ sót ảnh lỗi có thể ảnh hưởng chất lượng dữ liệu đầu ra; đưa nhiều ảnh hữu ích vào queue làm tiêu tốn budget review. Score chỉ thể hiện thứ tự ưu tiên, không phải xác suất ảnh có lỗi.

Đầu vào gồm `images.csv` và ảnh JPEG; đầu ra gồm `ranked_review.csv`, queue/contact sheet, audit log và quyết định GO/HOLD/REWORK. Baseline và PoC cùng xếp hạng đủ 96 ảnh, còn queue và metric chính thức cùng dùng **40 ảnh eval, B=20, seed=42**. 56 ảnh dev chỉ phục vụ hiệu chỉnh đặc trưng/ngưỡng.

QC chọn KEEP, RECAPTURE hoặc HOLD; các trạng thái được ánh xạ tương ứng sang GO, REWORK hoặc HOLD. Quyết định chỉ áp dụng cho **queue eval top-20**, không phê duyệt phát hành cả batch 96 ảnh. Repo chưa quy định ngưỡng Recall/Precision để được release; báo cáo không tự đặt một ngưỡng sau khi xem kết quả.

## 02 · Dữ liệu và provenance

| Split | Ảnh | Nhóm cảnh theo tiền tố image_id | Day | Dusk | Night | Nguồn / license |
|---|---:|---:|---:|---:|---:|---|
| dev | 56 | 14 | 36 | 16 | 4 | `fixtures/t02_raw_qc/`, synthetic, CC0-1.0 theo manifest |
| eval | 40 | 10 | 20 | 4 | 16 | Cùng fixture |
| Tổng | 96 | 24 | 56 | 20 | 20 | Ảnh 320×180; không dùng dữ liệu thật |

Metadata có `image_id`, `path`, `camera_id`, `light`, `split`. Nhãn dành cho evaluator theo contract gồm `defect_type ∈ {none, blur, glare, dark, compression}`, `severity` và `is_defect`; **`fixtures/t02_raw_qc/gt/labels.csv` không có trong bản repo hiện tại**. Không suy diễn nhãn từ hậu tố ID hoặc tạo GT thay thế.

Tài liệu đề mô tả split khoảng 60%/40% theo cảnh gốc; số đếm thực tế là 56/40 ảnh, tức 58,33%/41,67%. Các nhóm cảnh được nhận diện từ tiền tố ID để đối soát, phù hợp cấu trúc fixture; đây không phải nhãn chất lượng ảnh. Manifest T02 bao phủ metadata và 96 ảnh, ghi nguồn, license, split, group và SHA-256.

**Sự cố đã xử lý:** lần chạy cũ dừng do `hash_mismatch` ở `images.csv`. Kiểm tra byte cho thấy 170 tệp thuộc các fixture bị chuyển LF sang CRLF trong bản làm việc Windows. Với cả 170 tệp, chuyển CRLF về LF làm SHA-256 khớp chính xác manifest gốc. Riêng `images.csv` của T02 sau khôi phục có SHA-256:

```text
26a54d9de362b92139554efec64a2710586a8c2d58a23fd02f8c4ff4c93bd7c7
```

Công cụ [restore_fixture_newlines.py](../tools/restore_fixture_newlines.py) chỉ ghi lại tệp khi byte LF khớp hash đã có; gặp thay đổi khác sẽ dừng. Không thay hash manifest và không tắt `strict_provenance`. Quy tắc [.gitattributes](../.gitattributes) giữ LF cho tệp văn bản trong fixture khi checkout về sau. Kết quả chạy lại: **14 manifests, 0 failing**. Nội dung fixture so với Git không có thay đổi ngữ nghĩa.

**Dịch chuyển phân bố cần lưu ý:** night chỉ chiếm 4/56 ảnh dev (7,14%) nhưng chiếm 16/40 ảnh eval (40%). Chuẩn hóa toàn cục trên dev ít ảnh đêm có thể khiến ảnh đêm hợp lệ nhận score cao; đây là rủi ro quan trọng khi giải thích kết quả.

## 03 · Thiết kế và thuật toán

Luồng xử lý là kiểm tra provenance → đọc ảnh → đo đặc trưng → chuẩn hóa bằng dev → tính score → chọn top-20 eval → review theo cấp → lưu quyết định và bằng chứng. `src.main` bật offline guard và GT guard; các lượt chạy được báo cáo không dùng `--allow-gt-read`.

**Baseline:** dùng phương sai Laplacian toàn ảnh, ngưỡng q25 trên 56 ảnh dev là **222,3122**. Score tăng khi Laplacian thấp hơn ngưỡng, được chuẩn hóa theo khoảng từ min dev đến q25 và chặn trong [0,1]. Tất cả ảnh có Laplacian từ ngưỡng trở lên có score=0; baseline không xếp tiếp nhóm này theo độ nét.

**PoC:** kết hợp bốn tín hiệu giải thích được, đều chuẩn hóa theo dev:

| Tín hiệu | Đặc trưng | Chiều rủi ro | Ngưỡng dev | Trọng số |
|---|---|---|---:|---:|
| Blur | Phương sai Laplacian | Thấp hơn q25 | 222,3122 | 0,35 |
| Dark | Tỷ lệ pixel xám <30 | Cao hơn q75 | 0,00384115 | 0,20 |
| Glare | Tỷ lệ pixel xám >245 lớn nhất trong lưới 4×4 | Cao hơn q75 | 0,00527778 | 0,30 |
| Compression | Chênh lệch biên lưới JPEG 8 pixel với biên khác | Cao hơn q75 | 0,92491931 | 0,15 |

Với tín hiệu thấp là xấu: `risk = clip((q25 − x)/(q25 − min_dev), 0, 1)`. Với tín hiệu cao là xấu: `risk = clip((x − q75)/(max_dev − q75), 0, 1)`. Trường hợp mẫu dev hằng được xử lý riêng trong mã nguồn.

```text
score = 0.35 × risk_blur + 0.20 × risk_dark
      + 0.30 × risk_glare + 0.15 × risk_compression
```

`pred_defect_type` lấy tín hiệu có risk lớn nhất, không lấy đóng góp sau nhân trọng số. Vì vậy loại lỗi gợi ý và thành phần đóng góp lớn nhất vào score có thể khác nhau. `reason` giữ các risk để QC kiểm tra. `pred_action=REVIEW` khi score>0 là gợi ý máy; không thay thế KEEP/RECAPTURE/HOLD của người review.

Trọng số là heuristic có sẵn trong implementation; chưa có thí nghiệm chứng minh đây là trọng số tối ưu. PoC hiện chuẩn hóa toàn cục, chưa chuẩn hóa riêng theo camera/ánh sáng. Kết quả eval trong báo cáo không được dùng để thay trọng số hoặc ngưỡng.

## 04 · Baseline so với PoC

Hai lượt chạy cùng fixture, config nhóm, seed=42, offline guard, GT guard và budget=20. Bảng dưới lấy từ `run_info.json`, queue và decision của từng lượt; [bảng sinh tự động](operational_comparison.md) là nguồn đối soát.

| Chỉ tiêu | Baseline | PoC |
|---|---:|---:|
| Exit code | 0 | 0 |
| Ảnh được xếp hạng | 96 | 96 |
| Pool eval / budget | 40 / 20 | 40 / 20 |
| Runtime toàn pipeline | 1,3647 s | 2,0355 s |
| Runtime quy đổi / 100 ảnh | 1,4216 s | 2,1203 s |
| Đo feature và score / ảnh | 7,682 ms | 14,721 ms |
| Quyết định queue | HOLD | HOLD |
| Defect Recall@20 | Chưa có GT | Chưa có GT |
| Precision@20 | Chưa có GT | Chưa có GT |

Runtime toàn pipeline gồm các bước xử lý và xuất artifact, không bao gồm thao tác review tương lai. Đây là một lượt chạy cục bộ cho mỗi phương pháp, có chạy đồng thời với tác vụ kiểm tra khác; chưa đủ để kết luận về hiệu năng ổn định hoặc SLA.

Hai queue giao nhau **14/20 ảnh**; PoC đưa vào 6 ảnh khác so với baseline, Jaccard=14/26=**0,5385**. Điều này chứng minh thứ tự/ảnh được ưu tiên đã thay đổi, chưa chứng minh tăng độ chính xác.

**Hạn chế baseline quan sát được:** chỉ 7/40 ảnh eval có score>0; 33 ảnh còn lại đồng điểm 0. Để đủ B=20, baseline lấy thêm 13 ảnh từ nhóm đồng điểm theo thứ tự ổn định của đầu vào (`mergesort`). Vì vậy thứ hạng 8–40 của baseline chịu ảnh hưởng thứ tự metadata, không thể đọc như mức độ lỗi giảm dần.

Lệnh evaluator đã được thử cho cả hai output và đều trả **exit 2, ground truth file not found**. Chi tiết nằm trong `evaluation_attempts` của [results_summary.json](results_summary.json). Không tạo `metrics_baseline.json`, `metrics_poc.json` hoặc bảng metric chính thức khi evaluator chưa có GT.

## 05 · Protocol đánh giá

[Metric contract](metric_contract.md) dùng đúng `src.metrics.tracks::eval_t02`:

- **Primary:** Defect Recall@B = số ảnh GT có lỗi trong top-B / tổng số ảnh GT có lỗi trong eval; higher is better.
- **Kèm theo:** Precision@B = số ảnh GT có lỗi trong top-B / B, với B=20.
- Ghép theo `image_id`; lọc GT và prediction về split `eval`, sau đó sort score giảm dần, giữ thứ tự ổn định khi đồng điểm. Pool hiện có 40 ảnh theo metadata; N nhãn phải được xác nhận lại khi có GT.
- False alarm theo `light` = số ảnh GT sạch thuộc slice được chọn vào top-20 / tổng ảnh GT sạch trong slice. Tỷ lệ này khác tỷ lệ chọn ảnh của một slice.
- Defect-type accuracy được evaluator tính trên các ảnh GT có lỗi được ghép với prediction, không chỉ 20 ảnh được review. Recall theo `defect_type` cần GT; severity breakdown nằm ngoài scope đã chốt.

Khi có GT, chạy lệnh chính thức ở mục 08, báo cả numerator/denominator/N và kết quả bằng 0 hoặc kém hơn baseline. Khoảng tin cậy chưa được tính. Nếu bổ sung phân tích bất định, ưu tiên paired bootstrap theo cảnh gốc để giữ quan hệ giữa các biến thể cùng cảnh; với 10 cảnh eval, cần nêu rõ bất định lớn và không coi các biến thể là mẫu độc lập hoàn toàn.

## 06 · Kết quả theo slice và trường hợp cần kiểm tra

Bảng này là **độ phủ của queue theo metadata**, chưa phải recall, precision hoặc false alarm. Số liệu đầy đủ nằm trong [queue_slices.csv](queue_slices.csv).

| Slice | N eval | Baseline được chọn | PoC được chọn | Tỷ lệ chọn baseline → PoC |
|---|---:|---:|---:|---|
| Day | 20 | 8 | 8 | 40,00% → 40,00% |
| Dusk | 4 | 2 | 2 | 50,00% → 50,00% |
| Night | 16 | 10 | 10 | 62,50% → 62,50% |
| cam_A | 28 | 13 | 16 | 46,43% → 57,14% |
| cam_B | 12 | 7 | 4 | 58,33% → 33,33% |

PoC giữ nguyên số ảnh theo mỗi điều kiện sáng nhưng thay thành phần ảnh cụ thể. Queue PoC có ít ảnh cam_B hơn baseline; chưa thể gọi đây là giảm false alarm hoặc giảm thiên lệch khi chưa có nhãn. Đặc biệt, 10/20 vị trí của cả hai queue thuộc night, nên chưa có bằng chứng đã giải quyết rủi ro ưu tiên quá nhiều ảnh đêm.

Các hình dưới được xem trực tiếp và đối chiếu feature; mô tả là phân tích kỹ thuật, chưa phải nhãn QC hay GT.

### 6.1 · Vùng cháy sáng mà Laplacian toàn ảnh không ưu tiên

![img_17_2 — vùng trắng cháy sáng lớn trong ảnh ban ngày](../fixtures/t02_raw_qc/images/img_17_2.jpg)

`img_17_2` (day, cam_A) có Laplacian=465,073, cao hơn ngưỡng baseline; baseline score=0, hạng eval **34**. Một ô lưới glare có tỷ lệ bão hòa=1,0, PoC risk_glare=1,0, score=0,300, hạng **12** và được chọn vào queue. Ảnh cho thấy vùng cháy sáng lớn dù các vùng khác còn cạnh rõ. Đây là bằng chứng PoC có cơ chế ưu tiên tín hiệu glare mà baseline một đặc trưng thiếu; chưa phải số đo recall tăng.

### 6.2 · Ảnh đêm vẫn còn chi tiết nhưng bị ưu tiên vì độ tối

![img_13_0 — ảnh đêm vẫn còn các phương tiện và cấu trúc cảnh](../fixtures/t02_raw_qc/images/img_13_0.jpg)

`img_13_0` (night, cam_A) có Laplacian=2231,743 nhưng 54,16% pixel xám dưới 30. PoC gợi ý `dark`, score=0,12475, đưa ảnh từ hạng baseline **24** lên hạng **19**. Quan sát thấy vẫn còn cấu trúc đường và phương tiện, nên QC cần xác định mức tối có làm ảnh mất giá trị sử dụng hay chỉ phản ánh bối cảnh đêm. Root cause có thể là chuẩn hóa độ tối toàn cục với dev chỉ có 4 ảnh night. Chưa xác nhận đây là false alarm.

### 6.3 · Camera mềm và ảnh hưởng của đồng điểm

![img_06_0 — ảnh đêm cam_B với biên vật thể mềm](../fixtures/t02_raw_qc/images/img_06_0.jpg)

`img_06_0` (night, cam_B) có Laplacian=275,665, vẫn cao hơn ngưỡng blur 222,312. Baseline chọn ở hạng **20** dù score=0; PoC xếp hạng **22**, ngoài budget. Vì baseline nhận ảnh qua nhóm đồng điểm, trường hợp này không chứng minh baseline đã báo nhầm blur trên cam_B. Nó cho thấy cần tách tác động của độ nét, thứ tự metadata và budget trước khi kết luận về camera bias. Chưa có thống kê false alarm theo camera bằng GT.

### 6.4 · Tín hiệu nén đã có nhưng vẫn nằm ngoài budget

![img_16_3 — ảnh có khối nén và mất chi tiết](../fixtures/t02_raw_qc/images/img_16_3.jpg)

`img_16_3` có blockiness=2,54094, risk_compression=0,36245; PoC gợi ý `compression` nhưng score chỉ 0,05782, hạng **27** (baseline **31**), nên vẫn ngoài top-20. Trọng số compression=0,15 và các ảnh có risk dark/blur/glare cao hơn có thể làm tín hiệu này bị đẩy xuống. Khi có GT cần xác minh liệu đây có phải lỗi bị bỏ sót trong budget; không thay trọng số dựa trên ví dụ eval này trong lượt đánh giá hiện tại.

## 07 · Con người, audit và quyết định

Pipeline đã tạo [queue PoC](evidence/poc/review_queue.csv), [audit log](evidence/poc/audit_log.jsonl), [decision log](evidence/poc/decision_log.csv) và [decision.json](evidence/poc/decision.json). Contact sheet tương tác tại [out/poc/contact_sheet.html](../out/poc/contact_sheet.html); mở lại bằng lệnh chạy PoC nếu thư mục out chưa có. HTML là công cụ nhập liệu offline; chỉ sau khi export CSV và chạy lại pipeline thì quyết định mới được nhập và audit.

Luồng đã cài là **QC → Senior QC → Domain owner**. Chỉ mục được HOLD mới chuyển cấp. Mỗi quyết định cần reviewer, action, reason code, timestamp và thời lượng phiên; HOLD/RECAPTURE cần ghi chú, KEEP dùng `no_defect`. `review_stage`, `queue_id` và item ID được kiểm tra để tránh nhập sai queue. Import lặp không tạo lại sự kiện review giống nhau; chỉnh sửa hợp lệ được ghi override mới.

Trạng thái thực tế của PoC:

| Trường | Giá trị |
|---|---|
| Queue ID | `t02-qc-13a5be3b0d19` |
| QC / Senior QC / Domain owner đã review | 0 / 0 / 0 |
| Chưa giải quyết | 20/20 |
| Status / reason code | `HOLD` / `REVIEW_PENDING` |
| Owner | Lê Tuấn Khôi (group lead) |
| Phạm vi | `t02:eval-top-20:t02-qc-13a5be3b0d19` |

`review_session_seconds=0` phản ánh chưa nhập review, không phải con người đã hoàn thành tức thời. Test có kiểm tra escalation, override và GO khi tất cả KEEP, nhưng dữ liệu giả lập của test không được tính là bằng chứng review thực tế. Audit baseline còn giữ sự kiện lỗi provenance của lần chạy trước; lần chạy thành công mới được đối soát bằng `run_info.json`, không xóa lịch sử cũ.

Chính sách quyết định: còn mục PENDING/HOLD → HOLD; giải quyết hết nhưng có RECAPTURE → REWORK; toàn bộ 20 mục KEEP → GO. Không tự chuyển HOLD thành đã duyệt, kể cả ở cấp domain owner.

## 08 · Tái lập và kiểm thử

Chạy tại thư mục gốc repository. Các lệnh dưới dùng PowerShell và venv hiện có trên Windows; việc tái lập từ máy mới cần cài các dependency trong `requirements.txt` trước khi ngắt mạng.

```powershell
# Khôi phục byte LF nếu bản checkout cũ bị chuyển CRLF; xác minh hash.
.\.venv\Scripts\python -m tools.restore_fixture_newlines
.\.venv\Scripts\python -m tools.verify_manifests

# Hai lượt chạy dùng cùng seed và budget.
.\.venv\Scripts\python -m src.main --track t02 --pipeline src.baseline_t02 --output out/baseline --run-name baseline --offline --seed 42
.\.venv\Scripts\python -m src.main --track t02 --pipeline src.pipeline --output out/poc --run-name poc --offline --seed 42

# Kiểm thử; lưu log để công cụ báo cáo đếm số test.
.\.venv\Scripts\python -m pytest -q --basetemp out/pytest-report --tb=short -rA *> out/pytest_report.txt
.\.venv\Scripts\python -m tools.preflight *> out/preflight_report.txt

# Tổng hợp số liệu vận hành, snapshot và trạng thái evaluator.
.\.venv\Scripts\python -m tools.report_t02_results
```

`--basetemp out/pytest-report` dùng thư mục tạm trong workspace vì lượt pytest đầu tiên gặp lỗi quyền truy cập thư mục tạm mặc định của môi trường. Lượt kiểm tra sau khôi phục fixture và dùng basetemp này có **75 passed, 39 skipped, 0 failed, 0 errors**. 39 test bỏ qua đều cần overlay GT: 2 test CLI, 1 test common, 14 test manifest GT và 22 test evaluator. Không ghi nhận các test bị bỏ qua là đã pass.

Các kiểm tra có ý nghĩa bao gồm output contract offline; normalization bằng dev; feature glare/compression; lỗi hash, trùng ID, thiếu ảnh, đường dẫn thoát input; từ chối review sai stage/queue/action; escalation có lịch sử; import lặp và phạm vi GO chỉ áp dụng queue. Log đầy đủ tại [pytest_report.txt](evidence/pytest_report.txt). [Preflight](evidence/preflight_report.txt) đạt 0 FAIL; 2 WARN là thiếu `data/real` và `models_optional`, đều không cần cho PoC T02 này.

Lệnh chấm chính thức sau khi giảng viên cung cấp GT hợp lệ:

```powershell
.\.venv\Scripts\python -m src.evaluate --track t02 --gt fixtures/t02_raw_qc/gt/labels.csv --pred out/baseline/ranked_review.csv --run-name baseline --out reports/metrics_baseline.json --slices-out reports/slices_baseline.csv
.\.venv\Scripts\python -m src.evaluate --track t02 --gt fixtures/t02_raw_qc/gt/labels.csv --pred out/poc/ranked_review.csv --run-name poc --out reports/metrics_poc.json --slices-out reports/slices_poc.csv
.\.venv\Scripts\python -m src.compare reports/metrics_baseline.json reports/metrics_poc.json --out reports/table1_baseline_vs_poc.md
```

Hiện hai lệnh evaluate dừng với exit 2 do thiếu GT; `src.compare` chỉ chạy sau khi cả hai JSON metric được evaluator tạo thành công. Không sửa tay JSON metric hoặc bảng so sánh chính thức. GT phải ở gói giảng viên, không đưa lên repo công khai.

Môi trường đo: **Windows 11, Python 3.14.3**, processor string `Intel64 Family 6 Model 154 Stepping 3, GenuineIntel`; model CPU thương mại/RAM chưa được ghi nhận. Phiên bản package thực tế nằm trong `package_versions` của `results_summary.json`. Python này cao hơn dải 3.11–3.13 trong hướng dẫn starter; kiểm thử cục bộ đã chạy được, chưa xác nhận cùng kết quả trên các môi trường khác.

[Danh mục SHA-256 bằng chứng](evidence_manifest.csv) bảo vệ tính nhất quán của snapshot, bảng và dữ liệu chẩn đoán. `out/` bị Git ignore; các snapshot cần đọc báo cáo đã được lưu trong `reports/evidence/`.

## 09 · Giới hạn, quyền riêng tư và hướng tiếp theo

Dữ liệu được manifest khai báo là synthetic CC0-1.0, không sử dụng ảnh người thật hoặc PII thật trong thí nghiệm này. Cảnh synthetic có hình dạng biển số và phương tiện để minh họa, không dùng để khẳng định hiệu quả trên ảnh thật. Đây là PoC QC; chưa đánh giá chức năng ẩn danh hay tuân thủ pháp luật, không tuyên bố đạt GDPR hoặc luật Việt Nam.

Các giới hạn còn lại: tập eval chỉ 10 cảnh; các biến thể cùng cảnh có tương quan; phân bố night giữa dev/eval lệch rõ; ngưỡng và trọng số chưa được chứng minh tối ưu; loại lỗi gợi ý không phải nhãn chuẩn; baseline có nhiều đồng điểm; chưa đo thời gian review thật, false alarm hay Recall/Precision. Kết quả số ảnh theo camera/ánh sáng không thay cho đánh giá fairness hoặc độ chính xác.

Ưu tiên tiếp theo là nhận overlay GT từ giảng viên và chấm cùng protocol; QC review queue, export CSV vào `out/poc/review_queue_reviewed.csv` và chạy lại PoC, xử lý escalation đến khi có quyết định cuối. Những cải tiến như normalization theo camera/light, ROI glare và điều chỉnh cân bằng tín hiệu cần được thử trên dev hoặc tập phát triển mới rồi đánh giá trên heldout chưa dùng để tune. Kiểm tra 10 ảnh ngoài miền theo mốc +24h chưa được thực hiện vì chưa có dữ liệu phù hợp.

## 10 · Đóng góp và bằng chứng

Đối chiếu [team_contributions.csv](team_contributions.csv) với Git trên nhánh HEAD. Bảng phân biệt phần đã có bằng chứng và vai trò mới là phân công; không gán mã starter hoặc commit của tác giả nền tảng thành đóng góp của thành viên nhóm.

| Thành viên / danh tính Git | Vai trò | Bằng chứng thực tế | Giới hạn |
|---|---|---|---|
| Lê Tuấn Khôi / `KhoiLe` | Lead, tích hợp và implementation T02 | `13ef41c`: pipeline, baseline, review/contact sheet, image feature, test T02, demo, config; `4a2097e`, `1596eb9`, `7513a60`: tài liệu/đóng góp | Chưa có bằng chứng xác nhận ai đã trình bày |
| `quangts2531` — chưa xác nhận họ tên | Data & Provenance theo phân công | `1243d92`: cập nhật vai trò trong CSV đóng góp | Commit này chưa chứng minh implementation data/provenance |
| Trần Thị Ngọc Ánh / `Ngocanh203` | Core Algorithm & Baseline theo phân công | `ea586e8`: cập nhật tài liệu onboarding T02 | Implementation hiện được chứng minh bởi commit của KhoiLe |
| `Derr` — chưa xác nhận họ tên | Human Review & Audit theo phân công | `d774850`: sửa dấu câu docstring; `bc88bf6` rồi `8bc4d5e`: xóa và khôi phục `src/common/report.py`; `5ec9a72`: cập nhật bảng đóng góp | File report được khôi phục về nội dung đã có; chưa có lượt review thật được chứng minh |
| `Ngunhcho7654` — chưa xác nhận họ tên | Metric & Evaluation | `fe5afc4`: thêm 26 dòng chú thích tiếng Việt trong `src/metrics/tracks.py`; `6d254f9`: cập nhật bảng đóng góp | Đóng góp giải thích mã nguồn; không thay thuật toán metric, chưa xác nhận trình bày |
| Chưa xác nhận thành viên | QA & Reproducibility theo phân công | Chưa có commit riêng được xác nhận | Không phân bổ lại test của người khác thành đóng góp cá nhân |
| Chưa xác nhận thành viên | Demo & Documentation theo phân công | Chưa có commit riêng được xác nhận | Cần nhóm xác nhận danh tính và phần việc thực tế |

KhoiLe xuất hiện với hai email trong lịch sử (`tuankhoi000@gmail.com` và email GitHub noreply). Các tác giả nền tảng `Tin Duong`, `loversky02` và các tác giả xuất hiện ở nhánh khác trong `git shortlog --all` không tự động được xem là thành viên G02. [Trích lịch sử Git](evidence/git_contributions.txt) giữ lịch sử tại thời điểm chạy ban đầu; thông tin thành viên 4/5 được bổ sung khi ghép remote `ccd3f45` theo các commit nêu trong bảng. Commit báo cáo `204f5c0` được tạo với tác giả Git `vietluong3107`; chưa suy diễn họ tên/vai trò thành viên từ tài khoản này. Tên/email và bằng chứng trình bày của các thành viên chưa biết không được tự điền.

## 11 · Tài liệu và checklist bàn giao

| Tài liệu nội bộ | Ngày đối soát | Nội dung sử dụng |
|---|---|---|
| [T02.md](../docs/tracks/T02.md) | 14/11/2026 | Input/output, budget, metric và failure modes |
| [pipeline.py](../src/pipeline.py), [baseline_t02.py](../src/baseline_t02.py) | 14/11/2026 | Thuật toán và chính sách queue/decision thực tế |
| [image_ops.py](../src/common/image_ops.py) | 14/11/2026 | Định nghĩa Laplacian, dark, glare, blockiness |
| [tracks.py](../src/metrics/tracks.py), [evaluate.py](../src/evaluate.py) | 14/11/2026 | Công thức metric, split và xử lý thiếu GT |
| [test_t02_pipeline.py](../tests/test_t02_pipeline.py) | 14/11/2026 | Contract output, lỗi input, review và escalation |
| [logs.md](../logs.md) | 14/11/2026 | Quyết định về scope, severity và quy trình review |
| [report_t02_results.py](../tools/report_t02_results.py) | 14/11/2026 | Sinh bảng vận hành, slice, feature và snapshot |

- [x] Chạy baseline và PoC offline, xuất ranking/queue và decision.
- [x] Xác minh hash toàn bộ 14 fixture; ghi rõ nguyên nhân lỗi CRLF và cách khôi phục.
- [x] Có số mẫu, split, seed, budget, môi trường, runtime và bằng chứng kiểm thử.
- [x] Có so sánh vận hành, ít nhất hai slice và các ví dụ cần kiểm tra kèm ảnh/feature.
- [x] Giữ quyết định HOLD khi chưa có review, giới hạn scope ở eval top-20.
- [ ] Có GT hợp lệ, metric chính thức và `table1_baseline_vs_poc.md` do evaluator sinh.
- [ ] Có review thực tế, CSV reviewer, override/audit và quyết định sau review.
- [ ] Xác nhận đủ tên, đóng góp thực chất và bằng chứng trình bày của 7 thành viên.
- [ ] Tạo tag demo/final và xác nhận deadline theo hướng dẫn nộp bài.

Bản báo cáo đã hoàn thiện theo bằng chứng hiện có. Các mục chưa đạt được liệt kê rõ để nhóm bổ sung trước khi nộp/chấm chính thức; không thay thế dữ liệu thiếu bằng số liệu giả.
