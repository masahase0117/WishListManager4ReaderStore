import csv
import getpass
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def login_and_get_favorites():
    # ユーザー認証情報の取得
    username = input("ReaderStoreのメールアドレスを入力してください: ")
    password = getpass.getpass("パスワードを入力してください: ")

    # Seleniumの設定
    options = Options()
    # options.add_argument('--headless')  # ヘッドレスモードを使用する場合はコメントを外す
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)

    try:
        # ReaderStoreのログインページにアクセス
        driver.get("https://ebookstore.sony.jp/login/")

        # ログインフォームに認証情報を入力
        email_field = driver.find_element(
            By.ID, "email"
        )  # IDは実際のサイトに合わせて変更が必要
        password_field = driver.find_element(
            By.ID, "password"
        )  # IDは実際のサイトに合わせて変更が必要

        email_field.send_keys(username)
        password_field.send_keys(password)

        # ログインボタンをクリック
        login_button = driver.find_element(
            By.XPATH, "//button[@type='submit']"
        )  # XPATHは実際のサイトに合わせて変更が必要
        login_button.click()

        # ログイン後、お気に入りページに移動
        # お気に入りページのURLは実際のサイトに合わせて変更が必要
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[contains(@href, '/mypage')]")
            )
        )

        driver.get("https://ebookstore.sony.jp/mypage/wishlist/")

        # お気に入りリストの要素が読み込まれるまで待機
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".wishlist-item")
            )  # CSSセレクタは実際のサイトに合わせて変更が必要
        )

        # お気に入りリストの取得
        favorites = []
        wishlist_items = driver.find_elements(
            By.CSS_SELECTOR, ".wishlist-item"
        )  # CSSセレクタは実際のサイトに合わせて変更が必要

        for item in wishlist_items:
            try:
                title = item.find_element(By.CSS_SELECTOR, ".item-title").text
                author = item.find_element(By.CSS_SELECTOR, ".item-author").text
                price = item.find_element(By.CSS_SELECTOR, ".item-price").text

                # セール情報があれば取得
                try:
                    sale_price = item.find_element(By.CSS_SELECTOR, ".sale-price").text
                    is_on_sale = True
                except:
                    sale_price = ""
                    is_on_sale = False

                favorites.append(
                    {
                        "title": title,
                        "author": author,
                        "price": price,
                        "sale_price": sale_price,
                        "is_on_sale": is_on_sale,
                    }
                )
            except Exception as e:
                print(f"アイテムの処理中にエラーが発生しました: {e}")

        # 結果をCSVファイルに保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"readerstore_favorites_{timestamp}.csv"

        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["title", "author", "price", "sale_price", "is_on_sale"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for item in favorites:
                writer.writerow(item)

        print(f"お気に入りリストを {filename} に保存しました。")

        # 結果を表示
        print(f"\n合計 {len(favorites)} 件のお気に入りが見つかりました。")

        # セール対象の書籍を表示
        sale_items = [item for item in favorites if item["is_on_sale"]]
        if sale_items:
            print(f"\nセール対象の書籍 ({len(sale_items)} 件):")
            for item in sale_items:
                print(
                    f"- {item['title']} ({item['author']}) - 通常価格: {item['price']}, セール価格: {item['sale_price']}"
                )

        return favorites

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return []

    finally:
        # ブラウザを閉じる
        driver.quit()


def main() -> int:
    favorites = login_and_get_favorites()
    return 0 if favorites else 1


if __name__ == "__main__":
    main()
