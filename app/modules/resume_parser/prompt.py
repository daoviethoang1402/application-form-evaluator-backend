JSON_GENERATING_PROMPT = '''
Bạn sẽ được đưa **danh sách các hạng mục cần được trích xuất từ resume** ngay dưới đây. Nhiệm vụ của bạn là tạo ra một **mẫu JSON có thể được sử dụng để trích xuất các giá trị từ resume** tuân theo **hướng dẫn xây dựng mẫu JSON**, từ đó phục vụ cho việc đánh giá ứng viên tiềm năng. Cấu trúc của mẫu JSON này là: key là các trường cần được trích xuất, và value là giá trị được trích xuất từ resume.
Các hạng mục được táchh nhau bằng dấu phẩy. Các hạng mục con được tách nhau bằng dấu chấm phẩy. 
**danh sách các hạng mục cần được trích xuất từ resume**
--- BẮT ĐẦU DANH SÁCH ---
{required_fields}
--- KẾT THÚC DANH SÁCH ---

**hướng dẫn xây dựng mẫu JSON**
Mẫu JSON này chỉ bao gồm các hạng mục được yêu cầu, không được tự ý bổ sung thêm bất kỳ trường nào khác. Kể cả khi các hạng mục con có thể được bổ sung nhằm tăng ý nghĩa, nếu như không được yêu cầu thì bạn cũng không được tự ý bổ sung. 

Tôi sẽ bổ sung 2 ví dụ dưới đây để bạn có thể hiểu và làm theo.

--- BẮT ĐẦU VÍ DỤ 1 ---
**danh sách các hạng mục cần được trích xuất từ resume**
--- BẮT ĐẦU DANH SÁCH ---
học vấn và kinh nghiệm làm việc
--- KẾT THÚC DANH SÁCH ---

**mẫu JSON có thể được sử dụng để trích xuất các giá trị từ resume**
```json
{{“học vấn”:“”,“kinh nghiệm làm việc”:””,}}
```
--- KẾT THÚC VÍ DỤ 1 ---

--- BẮT ĐẦU VÍ DỤ 2 ---
**danh sách các hạng mục cần được trích xuất từ resume**
--- BẮT ĐẦU DANH SÁCH ---
học vấn: niên khóa, chuyên ngành, GPA; kinh nghiệm làm việc: vị trí, thời gian làm việc
--- KẾT THÚC DANH SÁCH ---
**mẫu JSON có thể được sử dụng để trích xuất các giá trị từ resume**
```json
{{học vấn”:{{“niên khóa”:“”,“chuyên ngành”:“”,“GPA”:“”,}},“kinh nghiệm làm việc”:{{“vị trí”:“”,“thời gian làm việc”:“”,}},}}
```
--- KẾT THÚC VÍ DỤ 2 ---
'''

QUERY_PROMPT = '''
Bạn sẽ được đưa **các hạng mục cần được trích xuất từ CV/resume**, **nội dung của CV/resume** và **mẫu JSON đóng vai trò làm output** ngay dưới đây. Nhiệm vụ của bạn là dựa trên **các hạng mục cần được trích xuất từ CV/resume**, hãy lấy các thông tin tương ứng trong **nội dung của CV/resume**, tuân theo **hướng dẫn trích xuất thông tin từ CV/resume** và trả về kết quả tuân theo **mẫu JSON đóng vai trò làm output**, từ đó phục vụ cho việc đánh giá ứng viên tiềm năng. 

**danh sách các hạng mục cần được trích xuất từ resume**
--- BẮT ĐẦU DANH SÁCH ---
{required_fields}
--- KẾT THÚC DANH SÁCH ---

**nội dung của CV/resume**
--- BẮT ĐẦU NỘI DUNG ---
{content}
--- KẾT THÚC NỘI DUNG ---

**mẫu JSON đóng vai trò làm output**
--- BẮT ĐẦU JSON---
{json_schema}
--- KẾT THÚC JSON---

**hướng dẫn trích xuất thông tin từ CV/resume**
1. Nếu một hạng mục không tồn tại, bạn tuyệt đối không được thay thế bằng bất cứ một hạng mục nào khác. Nếu như không có giá trị nào cho một trường nào đó, bạn hãy để trống trường đó trong mẫu JSON. 
2. Mẫu JSON được đưa chỉ bao gồm các hạng mục được yêu cầu. Bạn tuyệt đối không được tự ý bổ sung thêm bất kỳ hạng mục nào khác. Kể cả khi các hạng mục con có thể được bổ sung nhằm tăng ý nghĩa, nếu như không nằm trong mẫu JSON thì bạn cũng không được tự ý bổ sung.
3. (Exception) Đối với hai hạng mục “kinh nghiệm làm việc” (hoặc các từ ngữ tương đương) và “hoạt động ngoại khóa” (hoặc các từ ngữ tương đương), trong bối cảnh học sinh - sinh viên chưa đi làm thì hai hạng mục này có thể giống nhau. Nếu “hoạt động ngoại khóa” không tồn tại, nhưng lại tồn tại “kinh nghiệm làm việc” thì đây là trường hợp ngoại lệ duy nhất được phép chuyển đổi.
'''