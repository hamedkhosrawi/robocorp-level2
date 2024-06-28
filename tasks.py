from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    for item in orders:
        fill_form(item)
    """
    browser.configure(
        slowmo=1500,
    )
    download_csv_file()
    orders = get_orders()
    open_robot_order_website()
    for item in orders:
        fill_form(item)
    archive_receipts()
    

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('output/receipts/','receipts.zip',recursive=True)
    

  

def fill_form(order_rob):
    page = browser.page()
    page.select_option("#head",order_rob["Head"])
    radio_locator = find_radio_Btn(str(order_rob["Body"]))
    page.set_checked(radio_locator,True)
    page.fill("//input[@class='form-control' and @type='number']", str(order_rob["Legs"]))
    page.fill("//input[@class='form-control' and @name='address']",order_rob["Address"])
    page.click("button:text('Order')")
    
    #order_id =page.query_selector("//div[@id='receipt']/p[contains(@class,'badge-success')]").inner_text()
    order_id =page.locator("//div[@id='receipt']/p[contains(@class,'badge-success')]").inner_html()
    print(order_id)
    
    pdf_file = store_receipt_as_pdf(order_id)
    screenshot = screenshot_robot(order_id)
    embed_screenshot_to_receipt(screenshot, pdf_file)
    page.click("button:text('Order another robot')")
    close_annoying_modal()

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    screenshot_loc=screenshot+"x=200,y=500"
    list_of_files = [
        screenshot,
    ]
    print("screaanshotName= "+screenshot)
    print("pdfFileName= "+pdf_file)
    print(list_of_files)
    pdf.add_files_to_pdf(files=list_of_files,target_document=pdf_file)


def screenshot_robot(order_number):
    page = browser.page()
    screenshot_name = "output/receipts/screenshot_"+order_number+".png"
    print(screenshot_name)
    page.screenshot(path=screenshot_name)
    return screenshot_name


def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipts_results_html = page.locator("//div[@class='col-sm-7']/div[@id='order-completion']").inner_html()
    pdf = PDF()
    pdf_fileName= "output/receipts/receipts_"+order_number+".pdf"
    pdf.html_to_pdf(receipts_results_html, pdf_fileName)
    return pdf_fileName



def find_radio_Btn(body):
    page = browser.page()
    bodyList = []
    locator = ""
    bodyList = page.query_selector_all("input.form-check-input")
    for items in bodyList:
        value = str(items.get_property("value"))
        if(value == body):
            locator = "#id-body-"+value     
    return locator



def close_annoying_modal():
    page = browser.page()
    page.click("button:text('OK')")

def open_robot_order_website():
    browser.goto(url="https://robotsparebinindustries.com/#/robot-order")
    close_annoying_modal()

def download_csv_file():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)


def get_orders():
    library = Tables()
    orderList= []
    orders = library.read_table_from_csv("orders.csv",["Order number","Head","Body","Legs","Address"])
    for row in orders:
        
        orderList.append(row)
    
    return orderList
    

