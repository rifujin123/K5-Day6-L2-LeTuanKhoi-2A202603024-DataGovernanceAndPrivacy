# Onboarding — T02 Raw QC Triage

Tài liệu dành cho thành viên của nhóm G02: lấy mã nguồn, cài môi trường, chạy thử và tìm đúng kết quả để kiểm tra.

## 1. Dự án làm gì?

T02 ưu tiên ảnh nghi mờ, tối, lóa hoặc lỗi nén để annotator/QC xem trước. Công cụ tính score để xếp hạng; score không phải xác suất lỗi và không thay quyết định của con người.

- Dữ liệu hiện tại: 96 ảnh synthetic 320×180, gồm 56 ảnh dev và 40 ảnh eval, trong `fixtures/t02_raw_qc/`.
- Dev dùng để hiệu chỉnh ngưỡng/chuẩn hóa; queue lấy 20 ảnh có score cao nhất từ split eval.
- Baseline của nhóm: một ngưỡng Laplacian toàn ảnh, hiệu chỉnh trên dev.
- PoC: kết hợp blur, dark, glare và compression; chạy CPU/offline, không huấn luyện model.
- QC quyết định `KEEP`, `RECAPTURE` hoặc `HOLD`.

## 2. Đọc tài liệu nào trước?

| File | Nội dung |
|---|---|
| `README.md` | Contract chung, lệnh và quy định bài lab |
| `docs/tracks/T02.md` | Đề bài T02, dữ liệu, metric, failure modes |
| `configs/lab.yaml` | Cấu hình hiện tại của nhóm |
| `logs.md` | Lý do chọn phạm vi và các quyết định triển khai |
| `reports/group_report.md` | Kết quả đã báo cáo, bằng chứng và giới hạn |
| `reports/metric_contract.md` | Protocol đánh giá |
| `src/pipeline.py` | PoC, queue và chính sách quyết định |
| `src/baseline_t02.py` | Điểm vào baseline Laplacian của nhóm |
| `tests/test_t02_pipeline.py` | Kiểm thử riêng cho T02 |
| `reports/team_contributions.csv` | Ghi nhận đóng góp theo commit thực tế |

## 3. Chuẩn bị và lấy repo

Cần Git và Python. README starter hướng dẫn Python 3.11–3.13; ưu tiên Python 3.13 khi cài mới. Báo cáo nhóm ghi một môi trường Windows/Python 3.14.3 đã kiểm thử cục bộ, không có nghĩa mọi phiên bản Python đều được hỗ trợ.

Các lệnh dưới đây chạy trong **PowerShell**, tại thư mục gốc repo. Cần mạng khi clone và cài dependency; các lượt chạy baseline/PoC sau đó dùng chế độ offline.

```powershell
git clone https://github.com/rifujin123/K5-Day6-L2-LeTuanKhoi-2A202603024-DataGovernanceAndPrivacy.git
cd K5-Day6-L2-LeTuanKhoi-2A202603024-DataGovernanceAndPrivacy
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Nếu `py -3.13` không tìm thấy Python, cài Python 3.13 trước. Nếu đã clone repo, dùng thư mục hiện có; kiểm tra `git status` trước khi cập nhật để không làm mất thay đổi đang làm.

Không cần kích hoạt venv vì các lệnh gọi trực tiếp Python trong `.venv`.

## 4. Kiểm tra cấu hình và dữ liệu

Cấu hình hiện tại trong `configs/lab.yaml`:

```yaml
group_id: G02
owner: "Lê Tuấn Khôi (group lead)"
track_config: tracks/t02.yaml
track: t02
input: fixtures/t02_raw_qc
output: out/
seed: 42
offline: true
strict_provenance: true
params: {}
```

Người mới không cần đổi owner/group khi chỉ tái lập bài của nhóm.

```powershell
.\.venv\Scripts\python.exe -m tools.verify_manifests
.\.venv\Scripts\python.exe -m tools.preflight
```

Nếu bản checkout Windows cũ báo `hash_mismatch` do LF bị chuyển sang CRLF, báo cáo nhóm hướng dẫn dùng công cụ khôi phục rồi xác minh lại:

```powershell
.\.venv\Scripts\python.exe -m tools.restore_fixture_newlines
.\.venv\Scripts\python.exe -m tools.verify_manifests
```

Không sửa hash manifest hoặc tắt `strict_provenance` để bỏ qua lỗi. Nếu vẫn lỗi, đọc thông báo và kiểm tra đúng file liên quan. Theo báo cáo, thiếu `data/real` hoặc `models_optional` là cảnh báo về phần tùy chọn, không cần cho PoC T02 dùng fixture.

## 5. Chạy baseline và PoC

```powershell
.\.venv\Scripts\python.exe -m src.main --config configs/lab.yaml --track t02 --pipeline src.baseline_t02 --output out/baseline --run-name baseline --offline --seed 42
.\.venv\Scripts\python.exe -m src.main --config configs/lab.yaml --track t02 --pipeline src.pipeline --output out/poc --run-name poc --offline --seed 42
```

Hai lượt dùng cùng input, seed và budget. `make baseline TRACK=t02` trong Makefile gọi **random baseline mẫu**, không phải baseline Laplacian của nhóm; dùng lệnh `src.baseline_t02` ở trên để tái lập baseline trong báo cáo.

## 6. Tìm và kiểm tra kết quả

| Đường dẫn | Cần xem |
|---|---|
| `out/poc/ranked_review.csv` | Xếp hạng ảnh; có `image_id`, `score` và thông tin gợi ý |
| `out/poc/review_queue.csv` | Queue ưu tiên 20 ảnh eval |
| `out/poc/contact_sheet.html` | Giao diện review offline do pipeline sinh |
| `out/poc/audit_log.jsonl` | Nhật ký audit |
| `out/poc/decision.json` | Trạng thái, lý do, owner và phạm vi quyết định |
| `out/poc/decision_log.csv` | Nhật ký quyết định |
| `out/poc/run_info.json` | Thông tin lượt chạy |
| `out/baseline/` | Kết quả tương ứng của baseline |

Mở contact sheet trong trình duyệt:

```powershell
Start-Process .\out\poc\contact_sheet.html
```

Khi chưa nhập review, `HOLD / REVIEW_PENDING` là trạng thái chờ con người xử lý, không đồng nghĩa pipeline chạy lỗi. `GO` chỉ áp dụng queue eval top-20, không phê duyệt cả batch 96 ảnh.

## 7. Làm quen thao tác review

1. Mở `out/poc/contact_sheet.html`, nhập tên reviewer và xem ảnh cùng lý do, ánh sáng, camera.
2. Chọn `KEEP`, `RECAPTURE` hoặc `HOLD`; mỗi quyết định cần reason code. Dùng `no_defect` cho KEEP; HOLD/RECAPTURE cần ghi chú.
3. Export CSV, đặt file tải về đúng tên `out/poc/review_queue_reviewed.csv`.
4. Chạy lại lệnh PoC ở mục 5 để import review và ghi audit.
5. Mục HOLD chuyển sang Senior QC; nếu tiếp tục HOLD thì chuyển Domain owner. Các file HTML tương ứng là `senior_contact_sheet.html` và `domain_owner_contact_sheet.html`, trong cùng thư mục output. File import tương ứng là `senior_review_queue_reviewed.csv` và `domain_owner_review_queue_reviewed.csv`.

Giữ nguyên ID, stage và queue ID trong CSV export. Chỉ sau export và import lại pipeline thì quyết định mới được ghi nhận; thao tác trên HTML không tự cập nhật audit.

## 8. Chạy kiểm thử

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp out/pytest-onboarding --tb=short
```

`out/pytest-onboarding` là thư mục tạm dành riêng cho pytest, không đặt dữ liệu cần giữ trong đó. Chỉ ghi kết quả kiểm thử thực sự nhận được trên máy mình. Test cần GT có thể được skip khi không có overlay giảng viên; skip không phải pass.

## 9. Đánh giá chất lượng và giới hạn

- Metric chính: Defect Recall@20 trên eval; đi kèm Precision@20.
- GT chính thức không có trong repo học viên; pipeline không được đọc `gt/`.
- Chỉ chạy evaluator khi giảng viên đã cung cấp GT hợp lệ; xem lệnh ở mục 08 của `reports/group_report.md`.
- Không tự điền số liệu metric hoặc sửa JSON/bảng so sánh chính thức bằng tay.
- Báo cáo ngày 14/11/2026 ghi baseline/PoC chạy được, nhưng chưa có GT và chưa có review thực tế; chưa kết luận PoC tốt hơn baseline về chất lượng.
- Kết quả kiểm thử trong báo cáo thuộc lượt chạy được ghi trong báo cáo, không phải bằng chứng người đọc đã chạy lại.
- Không commit dữ liệu người thật/biển số thật chưa có quyền. Dùng fixture synthetic cho bước làm quen này.

## 10. Ghi nhận đóng góp

Đọc lại tài liệu, kiểm tra lệnh/đường dẫn và commit thay đổi thực chất. Sau đó điền dòng của mình trong `reports/team_contributions.csv`: tên tác giả Git, email Git, vai trò, file thực sự đã làm, SHA commit và mô tả bằng chứng. Không nhận code, demo hay kết quả kiểm thử của người khác là phần mình đã thực hiện.

Tài liệu onboarding này được đối chiếu với README, Makefile, cấu hình nhóm, đề T02, pipeline, baseline, logs và báo cáo nhóm đang có trên nhánh main ngày 14/11/2026. Khi triển khai thay đổi, cần cập nhật lại hướng dẫn tương ứng.
