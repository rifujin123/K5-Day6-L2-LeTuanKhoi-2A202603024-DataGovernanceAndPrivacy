# Báo cáo và bằng chứng T02

Bắt đầu từ [group_report.md](group_report.md). Bản báo cáo ngày 14/11/2026 ghi nhận baseline và PoC chạy thành công; metric chính thức còn chờ GT giảng viên và quyết định queue hiện HOLD vì chưa có review thực tế.

| Tệp | Nội dung / cách tạo |
|---|---|
| [group_report.md](group_report.md) | Báo cáo hoàn chỉnh theo bằng chứng hiện có, giới hạn và checklist còn lại |
| [metric_contract.md](metric_contract.md) | Định nghĩa metric, split, budget, đồng điểm và protocol |
| [team_contributions.csv](team_contributions.csv) | Đóng góp đối chiếu Git; phân biệt bằng chứng thực tế với phân công |
| [results_summary.json](results_summary.json) | Run info, decision, số test, phiên bản package, trạng thái manifest và evaluator |
| [operational_comparison.md](operational_comparison.md) | Bảng so sánh vận hành; chưa phải bảng metric chất lượng |
| [ranking_diagnostics.csv](ranking_diagnostics.csv) | Feature, risk, score và hạng eval của 40 ảnh cho phân tích ví dụ |
| [queue_slices.csv](queue_slices.csv) | N eval, số/tỷ lệ ảnh được chọn theo light và camera; không phải false alarm |
| [evidence_manifest.csv](evidence_manifest.csv) | SHA-256 của snapshot và bảng/dữ liệu sinh tự động |
| `evidence/baseline/`, `evidence/poc/` | Snapshot ranking, queue, run info, decision và log từ `out/` |
| [evidence/pytest_report.txt](evidence/pytest_report.txt) | 75 passed, 39 skipped do thiếu GT; không có failed/error |
| [evidence/preflight_report.txt](evidence/preflight_report.txt) | 0 FAIL, 2 WARN cho dữ liệu/model tùy chọn |
| [evidence/git_contributions.txt](evidence/git_contributions.txt) | Trích Git log trên HEAD để đối soát đóng góp |

Tái tạo các tệp chẩn đoán/snapshot sau khi chạy baseline, PoC và lưu log kiểm thử theo mục 08 của báo cáo:

```powershell
.\.venv\Scripts\python -m tools.report_t02_results
```

Công cụ không đọc GT để tính feature; nó gọi evaluator riêng để ghi lại trạng thái chấm. Khi thiếu GT, evaluator exit 2; công cụ vẫn xuất diagnostics và không tự điền metric chất lượng.

Các tệp `metrics_baseline.json`, `metrics_poc.json`, `slices_baseline.csv`, `slices_poc.csv` và `table1_baseline_vs_poc.md` chỉ xuất hiện sau khi được cung cấp GT và chạy evaluator/compare thành công. **Không sửa tay các số liệu hoặc dùng diagnostics thay metric chính thức.**

Mở [contact sheet PoC](../out/poc/contact_sheet.html) để review, export `review_queue_reviewed.csv`, đặt vào `out/poc/` rồi chạy lại PoC để nhập quyết định. Chưa có CSV reviewer thật trong snapshot hiện tại. Không tự điền reviewer hoặc xác nhận GO thay người review. Sau review, chạy lại công cụ tổng hợp và cập nhật diễn giải báo cáo.

`out/` bị Git ignore; `reports/evidence/` giữ bằng chứng để đọc cùng báo cáo khi chia sẻ repository. GT giảng viên phải tiếp tục nằm ngoài phần công khai.
