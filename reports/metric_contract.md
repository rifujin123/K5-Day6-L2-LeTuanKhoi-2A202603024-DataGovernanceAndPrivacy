# Metric contract — T02 Raw QC Triage

Contract được đối soát ngày **14/11/2026** theo cấu hình và evaluator hiện có. Baseline/PoC đã sinh prediction nhưng chưa có GT để chấm. Ngày đối soát này không phải bằng chứng đăng ký trước thí nghiệm ở mốc phút 30; repository chưa có bằng chứng thời điểm ký/chốt như vậy.

| Mục | Khai báo |
|---|---|
| Track | T02 · Raw QC Triage |
| Primary metric | `Defect Recall@B`, đúng tên trong `src.metrics.tracks::eval_t02` |
| Chiều tốt | Higher |
| Đơn vị | Ảnh |
| Recall numerator / denominator | Số ảnh GT lỗi trong top-B / tổng số ảnh GT lỗi thuộc eval |
| Metric đi kèm | `Precision@B` = số ảnh GT lỗi trong top-B / B |
| Ghép prediction với GT | Theo `image_id`; không dùng IoU |
| Candidate pool | 40 ảnh split `eval` theo metadata `fixtures/t02_raw_qc/images.csv`; xác nhận lại N từ GT khi được cung cấp |
| Budget | B=20, cùng baseline và PoC |
| Seed | 42 |
| Dev | 56 ảnh thuộc 14 nhóm cảnh theo tiền tố ID; chỉ dùng dev để chuẩn hóa/ngưỡng |
| Eval | 40 ảnh thuộc 10 nhóm cảnh; không dùng nhãn eval để tune |
| Baseline | Laplacian toàn ảnh; q25 dev=222,31221008; score bị chặn trong [0,1] |
| PoC | Dev-normalized blur/dark/glare/compression; trọng số lần lượt 0,35/0,20/0,30/0,15 theo implementation có sẵn |
| Đồng điểm | Score giảm dần, stable mergesort; giữ thứ tự đầu vào khi score bằng nhau |
| Đóng băng cấu hình | Giữ nguyên thuật toán/trọng số hiện có khi xem diagnostics; chưa có nhãn eval để chỉnh theo GT |
| Lỗi bỏ sót | Ảnh GT có lỗi không nằm trong top-20; chỉ tính khi có GT |
| False alarm theo light | Số ảnh GT sạch của slice được chọn top-20 / tổng ảnh GT sạch của slice |
| Slice chính thức | `light` (day/dusk/night) và `defect_type`; không thêm severity breakdown |
| Chỉ số loại lỗi | `Defect-type accuracy (GT defects)` trên các ảnh GT có lỗi được ghép prediction, không giới hạn top-20 |
| Diagnostics bổ sung | Số ảnh được chọn và tỷ lệ chọn theo light/camera; giao nhau của hai queue. Các số này không phải chất lượng dự đoán |
| Bất định | Chưa tính do thiếu GT; nếu bổ sung, paired bootstrap theo cảnh để giữ tương quan giữa các biến thể, nêu rõ chỉ có 10 cảnh eval |
| Runtime | `run_info.json`: toàn pipeline và quy đổi /100 ảnh; `process_ms_per_image`: đo feature + score; không gồm thao tác review của con người |
| Người phụ trách trong config | Lê Tuấn Khôi (group lead), G02 |

**Trạng thái kiểm chứng:** provenance đạt; baseline và PoC đều exit 0, xếp hạng đủ 96 ảnh và tạo queue 20 ảnh eval. Cả hai lượt `src.evaluate` trả exit 2 do không có `fixtures/t02_raw_qc/gt/labels.csv`. Vì vậy Recall, Precision, defect-type accuracy, false alarm và confidence interval đều **chưa có số liệu**. Không thay chúng bằng 0 và không dùng prediction hay quan sát ảnh làm GT chính thức.

Khi có GT hợp lệ, dùng các lệnh evaluate/compare trong [báo cáo nhóm, mục 08](group_report.md#08--tái-lập-và-kiểm-thử). JSON metric và bảng so sánh chính thức phải do script sinh. Nếu baseline=0, ghi rõ `baseline=0` thay vì báo phần trăm cải thiện không xác định. Chi tiết trạng thái các lệnh hiện tại ở [results_summary.json](results_summary.json).
