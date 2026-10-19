# Imputation & Univariate EDA Report

- Nguồn dữ liệu: `C:\Users\DELL\PROJECT_TEAM_DA\data\retrieved\sqlite_retrieved.csv`
- Kích thước ban đầu: 12133 dòng x 42 cột
- Số dòng sau chuẩn hóa và xóa trùng: 12133 (đã xóa 0 dòng trùng)
- Tổng giá trị thiếu trước xử lý: 241150
- Tổng giá trị thiếu sau xử lý: 13294

## 1. Missing value trước imputation (gồm cả token lỗi như unknown, n/a, rỗng)

| column | raw_nan_count | invalid_token_count | missing_count | missing_percentage |
|---|---|---|---|---|
| publication_date | 514 | 0 | 514 | 4.24 |
| type | 513 | 0 | 513 | 4.23 |
| category | 510 | 0 | 510 | 4.2 |
| link_book_page | 510 | 0 | 510 | 4.2 |
| subtitle | 6628 | 0 | 6628 | 54.63 |
| edition | 7450 | 22 | 7472 | 61.58 |
| author | 533 | 3 | 536 | 4.42 |
| discount | 523 | 0 | 523 | 4.31 |
| isSecondHand | 510 | 0 | 510 | 4.2 |
| publisher | 492 | 0 | 492 | 4.06 |
| published_country | 770 | 30 | 800 | 6.59 |
| imprint | 516 | 0 | 516 | 4.25 |
| language | 584 | 0 | 584 | 4.81 |
| no_of_pages | 1073 | 6 | 1079 | 8.89 |
| height | 524 | 0 | 524 | 4.32 |
| width | 526 | 0 | 526 | 4.34 |
| spine | 645 | 0 | 645 | 5.32 |
| weight | 510 | 0 | 510 | 4.2 |
| salesRank | 5339 | 0 | 5339 | 44 |
| short_blurb | 852 | 0 | 852 | 7.02 |
| long_blurb | 991 | 0 | 991 | 8.17 |
| blurbReview | 7087 | 1 | 7088 | 58.42 |
| Thương hiệu | 12130 | 0 | 12130 | 99.98 |
| original_price | 11623 | 0 | 11623 | 95.8 |
| discount_price | 11623 | 0 | 11623 | 95.8 |
| discount_percentage | 11623 | 0 | 11623 | 95.8 |
| rating | 11623 | 0 | 11623 | 95.8 |
| rating_count | 11623 | 0 | 11623 | 95.8 |
| llm_content | 12113 | 0 | 12113 | 99.84 |
| ID | 12113 | 0 | 12113 | 99.84 |
| Tên sách | 12113 | 0 | 12113 | 99.84 |
| Tác giả | 12113 | 0 | 12113 | 99.84 |
| Nhà xuất bản | 12113 | 0 | 12113 | 99.84 |
| Giá | 12113 | 0 | 12113 | 99.84 |
| Giá gốc | 12113 | 0 | 12113 | 99.84 |
| Giảm giá | 12113 | 0 | 12113 | 99.84 |
| Phần trăm giảm | 12113 | 0 | 12113 | 99.84 |
| Đánh giá | 12113 | 0 | 12113 | 99.84 |
| Số lượt đánh giá | 12113 | 0 | 12113 | 99.84 |

## 2. Chiến lược imputation và lý do

| column | dtype | missing_count | strategy | fill_value | reason |
|---|---|---|---|---|---|
| publication_date | datetime64[us] | 671 | skip |  | Cột ngày/thời gian; không tự động nội suy vì dữ liệu sách không mặc định là chuỗi thời gian |
| type | str | 513 | mode | Paperback | Biến phân loại có 19 nhóm; điền mode |
| category | str | 510 | mode | artanddesign | Biến phân loại có 28 nhóm; điền mode |
| link_book_page | str | 510 | skip |  | Cột định danh: giữ giá trị thiếu |
| subtitle | str | 6628 | constant | Unknown | Văn bản tự do/tên riêng; dùng Unknown |
| edition | str | 7472 | constant | Unknown | Có 437 nhóm hoặc quá nhiều nhóm; dùng Unknown |
| author | str | 536 | constant | Unknown | Văn bản tự do/tên riêng; dùng Unknown |
| discount | float64 | 523 | median | 2.57 | skew=12.35; phân phối lệch hoặc cần hạn chế ảnh hưởng của giá trị cực đoan |
| isSecondHand | float64 | 510 | mean | 0 | skew=0.00; phân phối gần đối xứng |
| publisher | str | 492 | constant | Unknown | Có 1181 nhóm hoặc quá nhiều nhóm; dùng Unknown |
| published_country | str | 800 | constant | Unknown | Có 65 nhóm hoặc quá nhiều nhóm; dùng Unknown |
| imprint | str | 516 | constant | Unknown | Có 1566 nhóm hoặc quá nhiều nhóm; dùng Unknown |
| language | str | 584 | constant | Unknown | Có 42 nhóm hoặc quá nhiều nhóm; dùng Unknown |
| no_of_pages | str | 1079 | constant | Unknown | Có 2407 nhóm hoặc quá nhiều nhóm; dùng Unknown |
| height | float64 | 524 | median | 184 | skew=1.47; phân phối lệch hoặc cần hạn chế ảnh hưởng của giá trị cực đoan |
| width | float64 | 526 | mean | 206.3 | skew=0.39; phân phối gần đối xứng |
| spine | float64 | 645 | median | 23 | skew=3.42; phân phối lệch hoặc cần hạn chế ảnh hưởng của giá trị cực đoan |
| weight | float64 | 510 | median | 398 | skew=4.44; phân phối lệch hoặc cần hạn chế ảnh hưởng của giá trị cực đoan |
| salesRank | float64 | 5339 | median | 6340 | skew=2.05; phân phối lệch hoặc cần hạn chế ảnh hưởng của giá trị cực đoan |
| short_blurb | str | 852 | constant | Unknown | Văn bản tự do/tên riêng; dùng Unknown |
| long_blurb | str | 991 | constant | Unknown | Văn bản tự do/tên riêng; dùng Unknown |
| blurbReview | str | 7088 | constant | Unknown | Văn bản tự do/tên riêng; dùng Unknown |
| Thương hiệu | str | 12130 | mode | Casio | Biến phân loại có 3 nhóm; điền mode |
| original_price | float64 | 11623 | median | 1.525e+05 | skew=4.03; phân phối lệch hoặc cần hạn chế ảnh hưởng của giá trị cực đoan |
| discount_price | float64 | 11623 | median | 3.466e+04 | skew=1.90; phân phối lệch hoặc cần hạn chế ảnh hưởng của giá trị cực đoan |
| discount_percentage | float64 | 11623 | mean | 21.68 | skew=-0.16; phân phối gần đối xứng |
| rating | float64 | 11623 | median | 5 | skew=-3.87; phân phối lệch hoặc cần hạn chế ảnh hưởng của giá trị cực đoan |
| rating_count | float64 | 11623 | median | 46.5 | skew=5.64; phân phối lệch hoặc cần hạn chế ảnh hưởng của giá trị cực đoan |
| llm_content | str | 12113 | constant | Unknown | Văn bản tự do/tên riêng; dùng Unknown |
| ID | float64 | 12113 | skip |  | Cột định danh: giữ giá trị thiếu |
| Tên sách | str | 12113 | mode | Sherlock Holmes | Biến phân loại có 12 nhóm; điền mode |
| Tác giả | str | 12113 | mode | Robin Sharma | Biến phân loại có 9 nhóm; điền mode |
| Nhà xuất bản | str | 12113 | mode | NXB Thế Giới | Biến phân loại có 6 nhóm; điền mode |
| Giá | float64 | 12113 | mean | 2.287e+05 | skew=-0.38; phân phối gần đối xứng |
| Giá gốc | float64 | 12113 | median | 3.169e+05 | skew=-0.61; phân phối lệch hoặc cần hạn chế ảnh hưởng của giá trị cực đoan |
| Giảm giá | float64 | 12113 | median | 6.381e+04 | skew=1.22; phân phối lệch hoặc cần hạn chế ảnh hưởng của giá trị cực đoan |
| Phần trăm giảm | float64 | 12113 | mean | 23.85 | skew=0.37; phân phối gần đối xứng |
| Đánh giá | float64 | 12113 | mean | 3.965 | skew=0.30; phân phối gần đối xứng |
| Số lượt đánh giá | float64 | 12113 | mean | 8672 | skew=0.20; phân phối gần đối xứng |

## 3. So sánh phân phối trước/sau (cùng tập dòng)

### Biến số

| column | before_count | after_count | mean_change_pct | median_change_pct | std_change_pct | assessment |
|---|---|---|---|---|---|---|
| gbpprice | 12133 | 12133 | 0 | 0 | 0 | OK |
| discount | 11610 | 12133 | -1.38 | 0 | -2.08 | OK |
| isSecondHand | 11623 | 12133 | nan | nan | nan | OK |
| height | 11609 | 12133 | -0.05 | 0 | -2.18 | OK |
| width | 11607 | 12133 | 0 | 0.13 | -2.19 | OK |
| spine | 11488 | 12133 | -0.27 | 0 | -2.67 | OK |
| weight | 11623 | 12133 | -1.01 | 0 | -1.97 | OK |
| salesRank | 6794 | 12133 | -13.48 | 0 | -23.78 | CẦN KIỂM TRA: phân phối thay đổi đáng kể |
| original_price | 510 | 12133 | -13.04 | 0 | -79.28 | CẦN KIỂM TRA: phân phối thay đổi đáng kể |
| discount_price | 510 | 12133 | -14.33 | 0 | -79.22 | CẦN KIỂM TRA: phân phối thay đổi đáng kể |
| discount_percentage | 510 | 12133 | 0 | -5.72 | -79.52 | CẦN KIỂM TRA: phân phối thay đổi đáng kể |
| rating | 510 | 12133 | 7.74 | 0 | -78.34 | CẦN KIỂM TRA: phân phối thay đổi đáng kể |
| rating_count | 510 | 12133 | -89.4 | 0 | -78.72 | CẦN KIỂM TRA: phân phối thay đổi đáng kể |
| Giá | 20 | 12133 | 0 | 0.76 | -96.04 | CẦN KIỂM TRA: phân phối thay đổi đáng kể |
| Giá gốc | 20 | 12133 | 5.23 | 0 | -96 | CẦN KIỂM TRA: phân phối thay đổi đáng kể |
| Giảm giá | 20 | 12133 | -11.88 | 0 | -95.98 | CẦN KIỂM TRA: phân phối thay đổi đáng kể |
| Phần trăm giảm | 20 | 12133 | -0 | 3.7 | -96.04 | CẦN KIỂM TRA: phân phối thay đổi đáng kể |
| Đánh giá | 20 | 12133 | 0 | 4.34 | -96.04 | CẦN KIỂM TRA: phân phối thay đổi đáng kể |
| Số lượt đánh giá | 20 | 12133 | -0 | -3.95 | -96.04 | CẦN KIỂM TRA: phân phối thay đổi đáng kể |

### Biến phân loại

| column | top_category_after | share_before_pct | share_after_pct | change_pp | assessment |
|---|---|---|---|---|---|
| type | Paperback | 62.72 | 66.95 | 4.23 | OK |
| category | artanddesign | 4.35 | 8.56 | 4.2 | OK |
| Thương hiệu | Casio | 0.01 | 99.98 | 99.98 | CẦN KIỂM TRA: mode-impute làm phình nhóm đầu |
| Tên sách | Sherlock Holmes | 0.02 | 99.86 | 99.84 | CẦN KIỂM TRA: mode-impute làm phình nhóm đầu |
| Tác giả | Robin Sharma | 0.03 | 99.87 | 99.84 | CẦN KIỂM TRA: mode-impute làm phình nhóm đầu |
| Nhà xuất bản | NXB Thế Giới | 0.05 | 99.88 | 99.84 | CẦN KIỂM TRA: mode-impute làm phình nhóm đầu |

**Cột cần kiểm tra:** `salesRank`, `original_price`, `discount_price`, `discount_percentage`, `rating`, `rating_count`, `Giá`, `Giá gốc`, `Giảm giá`, `Phần trăm giảm`, `Đánh giá`, `Số lượt đánh giá`, `Thương hiệu`, `Tên sách`, `Tác giả`, `Nhà xuất bản`

## 4. Thống kê mô tả và kết luận phân phối

| column | count | mean | median | std | skewness | kurtosis | distribution |
|---|---|---|---|---|---|---|---|
| gbpprice | 12133 | 5725 | 13.41 | 3.777e+04 | 14.37 | 355.9 | lệch phải (mạnh), đuôi dày; không chuẩn (Shapiro p=7.34e-93) |
| discount | 12133 | 3.727 | 2.57 | 5.44 | 12.61 | 355.7 | lệch phải (mạnh), đuôi dày; không chuẩn (Shapiro p=9.46e-83) |
| isSecondHand | 12133 | 0 | 0 | 0 | 0 | 0 | gần đối xứng |
| height | 12133 | 185.9 | 184 | 50.36 | 1.507 | 9.691 | lệch phải (mạnh), đuôi dày; không chuẩn (Shapiro p=5.22e-47) |
| width | 12133 | 206.3 | 206.3 | 49.42 | 0.3949 | 2.21 | gần đối xứng, đuôi dày; không chuẩn (Shapiro p=1.72e-29) |
| spine | 12133 | 24.19 | 23 | 12.59 | 3.528 | 35.75 | lệch phải (mạnh), đuôi dày; không chuẩn (Shapiro p=1.32e-52) |
| weight | 12133 | 517.8 | 398 | 449.5 | 4.553 | 50.74 | lệch phải (mạnh), đuôi dày; không chuẩn (Shapiro p=1.13e-70) |
| salesRank | 12133 | 7908 | 6340 | 7309 | 3.073 | 11.25 | lệch phải (mạnh), đuôi dày; không chuẩn (Shapiro p=2.14e-73) |
| original_price | 12133 | 1.535e+05 | 1.525e+05 | 3.185e+04 | 21.07 | 778.6 | lệch phải (mạnh), đuôi dày; không chuẩn (Shapiro p=1.44e-93) |
| discount_price | 12133 | 3.491e+04 | 3.466e+04 | 7266 | 11.2 | 249 | lệch phải (mạnh), đuôi dày; không chuẩn (Shapiro p=4.62e-92) |
| discount_percentage | 12133 | 21.68 | 21.68 | 2.015 | -0.7568 | 69.69 | lệch trái (vừa), đuôi dày; không chuẩn (Shapiro p=4.46e-91) |
| rating | 12133 | 4.984 | 5 | 0.2312 | -20.25 | 427.6 | lệch trái (mạnh), đuôi dày; không chuẩn (Shapiro p=6.05e-95) |
| rating_count | 12133 | 73.8 | 46.5 | 482 | 28.17 | 908.1 | lệch phải (mạnh), đuôi dày; không chuẩn (Shapiro p=4.83e-95) |
| Giá | 12133 | 2.287e+05 | 2.287e+05 | 3665 | -8.756 | 1738 | lệch trái (mạnh), đuôi dày; không chuẩn (Shapiro p=1.28e-95) |
| Giá gốc | 12133 | 3.169e+05 | 3.169e+05 | 4462 | -23.99 | 1874 | lệch trái (mạnh), đuôi dày; không chuẩn (Shapiro p=1.2e-95) |
| Giảm giá | 12133 | 6.382e+04 | 6.381e+04 | 2072 | 38.84 | 3245 | lệch phải (mạnh), đuôi dày; không chuẩn (Shapiro p=1.25e-95) |
| Phần trăm giảm | 12133 | 23.85 | 23.85 | 0.588 | 8.516 | 1151 | lệch phải (mạnh), đuôi dày; không chuẩn (Shapiro p=1.25e-95) |
| Đánh giá | 12133 | 3.965 | 3.965 | 0.02326 | 6.871 | 1212 | lệch phải (mạnh), đuôi dày; không chuẩn (Shapiro p=1.36e-95) |
| Số lượt đánh giá | 12133 | 8672 | 8672 | 258.7 | 4.651 | 1016 | lệch phải (mạnh), đuôi dày; không chuẩn (Shapiro p=1.26e-95) |

## 5. Outlier (IQR và Z-score > 3)

| column | iqr_outlier_count | iqr_outlier_pct | zscore_outlier_count | decision |
|---|---|---|---|---|
| gbpprice | 1343 | 11.07 | 233 | Tỷ lệ cao: phân phối lệch/đuôi dày, cân nhắc biến đổi log hoặc winsorize |
| discount | 672 | 5.54 | 120 | Tỷ lệ cao: phân phối lệch/đuôi dày, cân nhắc biến đổi log hoặc winsorize |
| isSecondHand | 0 | 0 | 0 | Không có outlier |
| height | 114 | 0.94 | 86 | Tỷ lệ thấp: giữ lại, kiểm tra thủ công giá trị cực đoan |
| width | 143 | 1.18 | 81 | Tỷ lệ thấp: giữ lại, kiểm tra thủ công giá trị cực đoan |
| spine | 334 | 2.75 | 95 | Tỷ lệ thấp: giữ lại, kiểm tra thủ công giá trị cực đoan |
| weight | 858 | 7.07 | 188 | Tỷ lệ cao: phân phối lệch/đuôi dày, cân nhắc biến đổi log hoặc winsorize |
| salesRank | 3838 | 31.63 | 393 | Tỷ lệ cao: phân phối lệch/đuôi dày, cân nhắc biến đổi log hoặc winsorize |
| original_price | 510 | 4.2 | 174 | Tỷ lệ thấp: giữ lại, kiểm tra thủ công giá trị cực đoan |
| discount_price | 510 | 4.2 | 244 | Tỷ lệ thấp: giữ lại, kiểm tra thủ công giá trị cực đoan |
| discount_percentage | 510 | 4.2 | 244 | Tỷ lệ thấp: giữ lại, kiểm tra thủ công giá trị cực đoan |
| rating | 217 | 1.79 | 44 | Tỷ lệ thấp: giữ lại, kiểm tra thủ công giá trị cực đoan |
| rating_count | 510 | 4.2 | 45 | Tỷ lệ thấp: giữ lại, kiểm tra thủ công giá trị cực đoan |
| Giá | 20 | 0.16 | 17 | Tỷ lệ thấp: giữ lại, kiểm tra thủ công giá trị cực đoan |
| Giá gốc | 20 | 0.16 | 18 | Tỷ lệ thấp: giữ lại, kiểm tra thủ công giá trị cực đoan |
| Giảm giá | 20 | 0.16 | 18 | Tỷ lệ thấp: giữ lại, kiểm tra thủ công giá trị cực đoan |
| Phần trăm giảm | 20 | 0.16 | 17 | Tỷ lệ thấp: giữ lại, kiểm tra thủ công giá trị cực đoan |
| Đánh giá | 20 | 0.16 | 19 | Tỷ lệ thấp: giữ lại, kiểm tra thủ công giá trị cực đoan |
| Số lượt đánh giá | 20 | 0.16 | 17 | Tỷ lệ thấp: giữ lại, kiểm tra thủ công giá trị cực đoan |
