# BandwidthBuddy

## English

### Overview
BandwidthBuddy is a Python-based application designed to monitor and manage network bandwidth usage for individual applications. It provides real-time monitoring, historical data analysis, and bandwidth limiting capabilities through an intuitive GUI built with PyQt6. The application supports multiple languages (English, Persian, and Chinese) and various themes for user customization.

### Features
- **Real-time Monitoring**: Displays current download and upload speeds for applications.
- **Historical Analysis**: View bandwidth usage over a specified time period with graphical representations (Bar, Line, Pie, Area).
- **Bandwidth Limiting**: Set download and upload limits for specific applications.
- **Multi-language Support**: Switch between English, Persian, and Chinese.
- **Customizable Themes**: Choose from Windows 11, Dark, Light, Red, and Blue themes.
- **Export Reports**: Export bandwidth usage data to CSV files.
- **Database Storage**: Uses SQLite to store bandwidth usage and limit settings.

### Requirements
- Python 3.8+
- PyQt6
- psutil
- matplotlib
- pandas
- numpy
- qdarkstyle

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/BandwidthBuddy.git
   cd BandwidthBuddy
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python bandwidth_buddy.py
   ```

### Usage
1. Launch the application to view the main window with two tabs: Real-time Monitoring and History.
2. In the Real-time Monitoring tab:
   - Select "All Apps" or "Individual Apps" to view bandwidth usage.
   - Choose a plot type (Bar, Line, Pie, Area) and time range (Last 10s, 1m, 5m, 1h).
   - Set bandwidth limits for specific applications using the "Set Bandwidth Limit" button.
3. In the History tab:
   - Filter data by date range and application.
   - View historical bandwidth usage in a table or generate a plot.
4. Use the menu bar to change language, theme, or export reports.

### Project Structure
- `bandwidth_buddy.py`: Main application script containing the GUI and monitoring logic.
- `bandwidth_buddy.db`: SQLite database for storing bandwidth usage and limit settings.
- `BandwidthBuddy.jpg`: Icon file for the application.

### License
This project is licensed under the MIT License.

---

## فارسی

### بررسی اجمالی
BandwidthBuddy یک برنامه مبتنی بر پایتون است که برای نظارت و مدیریت استفاده از پهنای باند شبکه برای برنامه‌های مختلف طراحی شده است. این برنامه قابلیت نظارت در زمان واقعی، تحلیل داده‌های تاریخی و محدود کردن پهنای باند را از طریق یک رابط کاربری گرافیکی بصری ساخته شده با PyQt6 ارائه می‌دهد. این برنامه از چندین زبان (انگلیسی، فارسی و چینی) و تم‌های مختلف برای سفارشی‌سازی کاربر پشتیبانی می‌کند.

### ویژگی‌ها
- **نظارت در زمان واقعی**: نمایش سرعت دانلود و آپلود فعلی برای برنامه‌ها.
- **تحلیل تاریخی**: مشاهده استفاده از پهنای باند در یک بازه زمانی مشخص با نمایش گرافیکی (میله‌ای، خطی، دایره‌ای، منطقه‌ای).
- **محدود کردن پهنای باند**: تنظیم محدودیت‌های دانلود و آپلود برای برنامه‌های خاص.
- **پشتیبانی از چند زبان**: امکان جابجایی بین انگلیسی، فارسی و چینی.
- **تم‌های قابل تنظیم**: انتخاب از میان تم‌های ویندوز ۱۱، تیره، روشن، قرمز و آبی.
- **صادرات گزارش‌ها**: صادرات داده‌های استفاده از پهنای باند به فایل‌های CSV.
- **ذخیره‌سازی پایگاه داده**: استفاده از SQLite برای ذخیره داده‌های استفاده از پهنای باند و تنظیمات محدودیت.

### پیش‌نیازها
- پایتون ۳.۸ یا بالاتر
- PyQt6
- psutil
- matplotlib
- pandas
- numpy
- qdarkstyle

### نصب
1. مخزن را کلون کنید:
   ```bash
   git clone https://github.com/yourusername/BandwidthBuddy.git
   cd BandwidthBuddy
   ```
2. وابستگی‌ها را نصب کنید:
   ```bash
   pip install -r requirements.txt
   ```
3. برنامه را اجرا کنید:
   ```bash
   python bandwidth_buddy.py
   ```

### استفاده
1. برنامه را اجرا کنید تا پنجره اصلی با دو تب نمایش داده شود: نظارت در زمان واقعی و تاریخچه.
2. در تب نظارت در زمان واقعی:
   - گزینه "همه برنامه‌ها" یا "برنامه‌های تکی" را برای مشاهده استفاده از پهنای باند انتخاب کنید.
   - نوع نمودار (میله‌ای، خطی، دایره‌ای، منطقه‌ای) و بازه زمانی (۱۰ ثانیه آخر، ۱ دقیقه، ۵ دقیقه، ۱ ساعت) را انتخاب کنید.
   - با استفاده از دکمه "تنظیم محدودیت پهنای باند"، محدودیت‌های پهنای باند را برای برنامه‌های خاص تنظیم کنید.
3. در تب تاریخچه:
   - داده‌ها را بر اساس بازه زمانی و برنامه فیلتر کنید.
   - استفاده تاریخی از پهنای باند را در جدول مشاهده کنید یا یک نمودار تولید کنید.
4. از نوار منو برای تغییر زبان، تم یا صادرات گزارش‌ها استفاده کنید.

### ساختار پروژه
- `bandwidth_buddy.py`: اسکریپت اصلی برنامه شامل رابط کاربری گرافیکی و منطق نظارت.
- `bandwidth_buddy.db`: پایگاه داده SQLite برای ذخیره داده‌های استفاده از پهنای باند و تنظیمات محدودیت.
- `BandwidthBuddy.jpg`: فایل آیکون برنامه.

### مجوز
این پروژه تحت مجوز MIT منتشر شده است.

---

## 中文

### 概述
BandwidthBuddy 是一款基于 Python 的应用程序，旨在监控和管理各个应用程序的网络带宽使用情况。它通过使用 PyQt6 构建的直观图形用户界面提供实时监控、历史数据分析和带宽限制功能。该应用程序支持多种语言（英语、波斯语和中文）以及多种主题供用户自定义。

### 功能
- **实时监控**：显示应用程序当前的下载和上传速度。
- **历史分析**：查看指定时间段内的带宽使用情况，并以图形方式展示（柱状图、折线图、饼图、区域图）。
- **带宽限制**：为特定应用程序设置下载和上传限制。
- **多语言支持**：可在英语、波斯语和中文之间切换。
- **可自定义主题**：可选择 Windows 11、深色、浅色、红色和蓝色主题。
- **导出报告**：将带宽使用数据导出为 CSV 文件。
- **数据库存储**：使用 SQLite 存储带宽使用情况和限制设置。

### 要求
- Python 3.8 或更高版本
- PyQt6
- psutil
- matplotlib
- pandas
- numpy
- qdarkstyle

### 安装
1. 克隆仓库：
   ```bash
   git clone https://github.com/yourusername/BandwidthBuddy.git
   cd BandwidthBuddy
   ```
2. 安装依赖项：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行应用程序：
   ```bash
   python bandwidth_buddy.py
   ```

### 使用方法
1. 启动应用程序以查看包含两个选项卡的主窗口：实时监控和历史记录。
2. 在实时监控选项卡中：
   - 选择“所有应用程序”或“单个应用程序”以查看带宽使用情况。
   - 选择图表类型（柱状图、折线图、饼图、区域图）和时间范围（最近 10 秒、1 分钟、5 分钟、1 小时）。
   - 使用“设置带宽限制”按钮为特定应用程序设置带宽限制。
3. 在历史记录选项卡中：
   - 根据日期范围和应用程序过滤数据。
   - 在表格中查看历史带宽使用情况或生成图表。
4. 使用菜单栏更改语言、主题或导出报告。

### 项目结构
- `bandwidth_buddy.py`：包含图形用户界面和监控逻辑的主应用程序脚本。
- `bandwidth_buddy.db`：用于存储带宽使用情况和限制设置的 SQLite 数据库。
- `BandwidthBuddy.jpg`：应用程序的图标文件。

### 许可证
本项目采用 MIT 许可证。