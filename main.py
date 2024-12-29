import csv
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json


# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelno)s - %(message)s')

# 读取 CSV 文件的路径
file_path = 'problem.csv'
# 登录信息
luogu_username = ""

output_data = []

# 参数
ok_time = 0
simple_waittime = 3
long_waittime = 5
def create_driver():
    """
    创建并配置 Edge 浏览器驱动

    Returns:
        webdriver.Edge: 配置好的 Edge 浏览器驱动实例
    """
    try:
        driver = webdriver.Edge({})
        return driver
    except Exception as e:
        logging.error(f"创建浏览器驱动时出错: {e}")
        return None


def login(driver,luogu_keywords):
    """
    登录洛谷网站的函数

    Args:
        driver (webdriver.Edge): 浏览器驱动实例
    """
    if driver is None:
        logging.error("驱动未创建，无法登录")
        return
    login_url = "https://www.luogu.com.cn/auth/login"
    try:
        driver.get(login_url)
        # 设置显式等待，最长等待15秒，直到元素可被定位到（这里根据ID定位元素）
        wait = WebDriverWait(driver, 15)
        # 定位用户名输入框并输入用户名
        # 通过class和placeholder属性结合来定位用户名输入框所在的div，再找到内部input元素
        username_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.refined-input.input-wrap.form-input.frame[placeholder="用户名、手机号或电子邮箱"]')))
        username_input = username_div.find_element(By.TAG_NAME, 'input')
        username_input.send_keys(luogu_username)

        # 定位密码输入框并输入密码
        # 同样利用class和placeholder属性定位密码输入框所在div及内部input元素
        password_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.refined-input.input-wrap.form-input.frame[placeholder="密码"]')))
        password_input = password_div.find_element(By.TAG_NAME, 'input')
        password_input.send_keys(luogu_keywords)

        # 定位验证码输入框并输入验证码（这里假设手动输入验证码，如需自动识别需另做处理）
        captcha_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.refined-input.input-wrap.frame[placeholder="右侧图形验证码"]')))
        captcha_input = captcha_div.find_element(By.TAG_NAME, 'input')
        time.sleep(9)
        captcha_input.send_keys("")

        # 定位登录按钮并点击
        # 通过class属性定位登录按钮
        login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-login')))
        login_button.click()

        # 等待几秒，简单判断登录是否成功（更严谨的验证方式可按实际页面调整）
        time.sleep(simple_waittime)
        # 尝试定位name为gotorandom的元素来验证登录是否成功
        try:
            gotorandom_element = driver.find_element(By.NAME, 'gotorandom')
            logging.info("登录成功")
        except Exception as e:
            logging.error("登录可能失败，请检查用户名、密码、验证码及网络等情况")
    except Exception as e:
        logging.error(f"登录过程中出现错误: {e}")


def check_submit(driver, problemid):
    """
    检查是否可提交的函数

    Args:
        driver (webdriver.Edge): 浏览器驱动实例
        problemid (str): 题目 ID

    Returns:
        str: 表示是否可提交的标记，"can" 表示可提交，"cannot" 表示不可提交
    """
    if driver is None:
        return "cannot"
    url = "https://www.luogu.com.cn/problem/solution/" + problemid
    try:
        driver.get(url)
        # 增加等待时间，设置为 simple_waittime 秒
        submit_button = WebDriverWait(driver, simple_waittime).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a.l-button.lform-size-middle.button-transparent'))
        )
        return "can"
    except Exception as e:
        logging.error(f"检查是否可提交 {problemid} 时出错: {e}")
        return "cannot"


def read_csv(file_path):
    """
    读取 CSV 文件的函数。

    参数:
    file_path (str): 要读取的 CSV 文件的路径。

    返回:
    list: 包含 CSV 文件内容的列表，每个元素是 CSV 文件的一行，以列表形式存储。
    """
    problem_ids = []
    header = None
    try:
        # 以只读模式打开文件
        with open(file_path, mode='r') as file:
            # 创建 CSV 读取器对象
            csv_reader = csv.reader(file)
            try:
                header = next(csv_reader)  # 存储第一行（表头）
            except StopIteration:
                pass  # 如果没有更多行，跳过存储表头操作
            # 遍历 CSV 读取器并添加满足条件的行到 problem_ids 列表
            for row in csv_reader:
                
                if len(row) >= 2:  # 确保行有至少两列
                    try:
                        first_column_value = float(row[0])
                        if first_column_value <= ok_time:
                            problem_ids.append(row[1])
                        else:
                            output_data.append(row)
                    except ValueError:
                        logging.error(f"无法将 {row[0]} 转化为浮点数")
    except FileNotFoundError:
        logging.error(f"文件 {file_path} 不存在，将创建一个空的文件。")
        try:
            # 以写入模式创建一个空文件
            with open(file_path, mode='w', newline=''):
                pass
        except PermissionError:
            logging.error(f"没有权限创建文件 {file_path}，请检查权限设置。")
    return problem_ids, header


def write_csv(file_path, data, header):
    """
    写入 CSV 文件的函数。

    参数:
    file_path (str): 要写入的 CSV 文件的路径。
    data (list): 包含要写入 CSV 文件的数据的列表，每个元素是一行，以列表形式存储。
    header (list): CSV 文件的表头
    """
    try:
        # 以写入模式打开文件
        with open(file_path, mode='w', newline='') as file:
            # 创建 CSV 写入器对象
            csv_writer = csv.writer(file)
            if header:
                csv_writer.writerow(header)  # 先写入表头
            # 遍历数据列表并将每一行写入文件
            for row in data:
                csv_writer.writerow(row)
        return 1
    except PermissionError:
        logging.error(f"没有权限写入文件 {file_path}，请检查权限设置。")
        return 0


def write_csv2(file_path, data, data2, header):
    """
    写入 CSV 文件的函数。

    参数:
    file_path (str): 要写入的 CSV 文件的路径。
    data (list): 包含要写入 CSV 文件的数据的列表，每个元素是一行，以列表形式存储。
    header (list): CSV 文件的表头
    """
    try:
        # 以写入模式打开文件
        with open(file_path, mode='w', newline='') as file:
            # 创建 CSV 写入器对象
            csv_writer = csv.writer(file)
            if header:
                csv_writer.writerow(header)  # 先写入表头
            # 遍历数据列表并将每一行写入文件
            for row in data:
                csv_writer.writerow(row)
            for i in data2:
                csv_writer.writerow([-404,i])
        return 1
    except PermissionError:
        logging.error(f"没有权限写入文件 {file_path}，请检查权限设置。")
        return 0


difficulty_name = ['暂未评定','入门','普及-','普及/提高-','普及+/提高','提高+/省选-','省选/NOI-','NOI/NOI+/CTSC']
def main():
    
    # 读取文件数据
    problem_ids, header = read_csv(file_path)
    print(f"读取的 {len(problem_ids)} 个题目 ID:")
    print(problem_ids)
    print(f"预计花费：{len(problem_ids)*long_waittime+10}s")
    if(len(problem_ids)==0):
        print("未读取到有效题目！")
        return
    
    try:
        luogu_keywords = str(header[7])
        logging.info(f"读到密码，长度为{len(luogu_keywords)}")
    except Exception as e:
        luogu_keywords = ""
        logging.error(f"获取密码出错，您需要将其放置在题目csv文件的1H位置，请检查放置。{e}")
        return
    driver = create_driver()
    login(driver,luogu_keywords)
    if driver is None:
        return
    cnt = 0
    for problemid in problem_ids:
        cnt=cnt+1
        
        # 访问 solution 页面
        solution_url = "https://www.luogu.com.cn/problem/solution/" + problemid
        try:
            driver.get(solution_url)
            script_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'lentille-context')))
            json_text = script_element.get_attribute('innerHTML')
            json_data = json.loads(json_text)
            count_value = json_data['data']['solutions']['count']
            submis_value = check_submit(driver, problemid)

            # 访问 problem 页面获取难度信息
            problem_url = "https://www.luogu.com.cn/problem/" + problemid
            driver.get(problem_url)
            # 定位包含难度信息的 a 元素
            difficulty_element = WebDriverWait(driver, simple_waittime).until(EC.presence_of_element_located(
                (By.XPATH, "//a[@data-v-0640126c and @data-v-263e39b8 and @data-v-1143714b and contains(@href, 'difficulty')]")
            ))
            href_value = difficulty_element.get_attribute('href')
            # 提取difficulty的值
            if 'difficulty=' in href_value:
                difficulty_value = href_value.split('difficulty=')[1].split('&')[0]
            else:
                difficulty_value = ""

            # 检查网页标题
            if driver.title == "错误 - 洛谷 | 计算机科学教育新生态":
                timestamp = 999999999999999999
                count_value = "not found"
            else:
                timestamp = time.time()
            output = f"No.{cnt}:{problemid},{count_value},{difficulty_value},{submis_value}"
            print(f"{timestamp}: {output}")
            # 分列保存数据
            output_data.append([timestamp, problemid, count_value, difficulty_value, difficulty_name[int(difficulty_value)], submis_value])
        except Exception as e:
            logging.error(f"处理题目 {problemid} 时出错: {e}")
            # if("web view not found" in e):
            #   logging.error(f"浏览器窗口可能已被关闭")
        time.sleep(long_waittime)
        if(cnt%3==0):
            try:
                tmp = write_csv2(file_path,output_data,problem_ids[cnt:],header)
                if(tmp==1):
                    print("自动保存成功")
                else:
                    print("自动保存失败")
            except Exception as e:
                logging.error(f"自动保存失败: {e}")

    
    if(write_csv(file_path, output_data, header)==0):
        logging.warning("将在20秒后重试")
        time.sleep(20)
        if(write_csv(file_path,output_data,header)==0):
            logging.error("保存失败")
            return
    print("保存成功，程序结束，即将关闭浏览器")
    time.sleep(5)
    
    # 关闭浏览器驱动
    try:
        driver.quit()
    except Exception as e:
        logging.error(f"关闭浏览器驱动时出错: {e}")


if __name__ == "__main__":
    main()
