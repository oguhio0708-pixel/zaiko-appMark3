import flet as ft
import psycopg2
import math
import os

# ==========================================
# 1. データベース設定と操作関数 (Supabase/PostgreSQL対応版)
# ==========================================
# 【重要】ここにSupabaseで取得したURIを貼り付けます。
# ※ [YOUR-PASSWORD] をご自身のパスワードに変更してください。
DB_URI = os.environ.get("DATABASE_URL", "postgresql://postgres.pixsxswdcaoggusfgbhv:Hionatamawari%402379070897@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres")

def get_conn():
    # クラウドのデータベースに接続します
    return psycopg2.connect(DB_URI)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (item_name TEXT PRIMARY KEY, current_stock REAL, lot_size REAL DEFAULT 1.0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS presets (preset_name TEXT, item_name TEXT, required_amount REAL, PRIMARY KEY(preset_name, item_name))''')
    
    c.execute("SELECT COUNT(*) FROM inventory")
    if c.fetchone()[0] == 0:
        default_items = [
            ("S板(枚)", 0.0, 40.0), ("L板(枚)", 0.0, 40.0), ("M板(枚)", 0.0, 40.0),
            ("チーズ(箱)", 0.0, 1.0), ("トマソ(パック)", 0.0, 6.0), ("バジソ(パック)", 0.0, 1.0),
            ("燻ベーコン(パック)", 0.0, 1.0), ("ハム(パック)", 0.0, 1.0), ("イタソ(パック)", 0.0, 1.0),
            ("ペパロニ(パック)", 0.0, 1.0), ("コーン(缶)", 0.0, 24.0), ("ハラピ(缶)", 0.0, 24.0),
            ("コーングリッツ(KG)", 0.0, 10.0), ("パイナップル(缶)", 0.0, 24.0), ("スラポ(パック)", 0.0, 1.0),
            ("マヨソース(本)", 0.0, 1.0), ("カマソ(パック)", 0.0, 1.0), ("パセリ(パック)", 0.0, 1.0),
            ("アラソ(パック)", 0.0, 1.0), ("ガーリック(パック)", 0.0, 1.0), ("プラックペッパー(パック)", 0.0, 1.0),
            ("ポッコン(袋)", 0.0, 1.0), ("カマンベールチーズ固形(袋)", 0.0, 1.0), ("オイル(本)", 0.0, 1.0),
            ("カルビ(パック)", 0.0, 1.0), ("ストチ(ホテルパン)", 0.0, 3.0), ("チェリトマ(パック)", 0.0, 1.0),
            ("バジル(パック)", 0.0, 1.0), ("ビーフ(パック)", 0.0, 1.0), ("BBQソース(パック)", 0.0, 1.0),
            ("パルメザンチーズ(袋)", 0.0, 1.0), ("ローチ(袋)", 0.0, 1.0), ("イースト(パック)", 0.0, 1.0),
            ("プレミックス(袋)", 0.0, 1.0), ("チェダーソース(パック)", 0.0, 1.0), ("大海老(パック)", 0.0, 1.0),
            ("チキテリ(パック)", 0.0, 1.0), ("コーラ15L(本)", 0.0, 6.0), ("コーラゼロ15L(本)", 0.0, 6.0),
            ("コーラ500(本)", 0.0, 24.0), ("コーラゼロ500(本)", 0.0, 24.0), ("クー(本)", 0.0, 24.0),
            ("爽健美茶(本)", 0.0, 24.0), ("ジンジャー(本)", 0.0, 24.0), ("ドクペ(本)", 0.0, 24.0),
            ("スプライト(本)", 0.0, 24.0), ("パルメザン小袋(個)", 0.0, 20.0), ("骨付き(パック)", 0.0, 1.0),
            ("ポテトフライ(パック)", 0.0, 6.0), ("ナゲット(パック)", 0.0, 1.0), ("ナゲットソース(個)", 0.0, 50.0),
            ("ケチャップ(個)", 0.0, 40.0), ("タバスコ(本)", 0.0, 12.0), ("シーザー(個)", 0.0, 50.0),
            ("クルトン(個)", 0.0, 20.0), ("カスパイ(個)", 0.0, 30.0), ("粉糖(パック)", 0.0, 1.0),
            ("サウザン(個)", 0.0, 50.0), ("コンソメ(パック)", 0.0, 1.0), ("チリガーリック(パック)", 0.0, 1.0),
            ("コンポタ(個)", 0.0, 10.0), ("くらむ(個)", 0.0, 10.0), ("エッグタルト(個)", 0.0, 20.0),
            ("からあげ(パック)", 0.0, 1.0), ("ディップソース(本)", 0.0, 1.0), ("アイス(箱)", 0.0, 1.0),
            ("牛乳(パック)", 0.0, 1.0), ("チョコソース(本)", 0.0, 1.0), ("ホイップ(パック)", 0.0, 1.0),
            ("フォンダン(パック)", 0.0, 1.0), ("ストロベリー(パック)", 0.0, 1.0), ("チーズ棒(箱)", 0.0, 1.0),
            ("ザクチキ(パック)", 0.0, 1.0), ("レッドブル(本)", 0.0, 24.0), ("オニオン(パック)", 0.0, 1.0),
            ("マッシュ(パック)", 0.0, 1.0), ("サラダ(パック)", 0.0, 1.0), ("ほうれん草(パック)", 0.0, 1.0),
            ("ピーマン(パック)", 0.0, 1.0), 
            ("ピザボックスS(箱)", 0.0, 1.0), ("ピザボックスM(箱)", 0.0, 1.0), ("ピザボックスL(箱)", 0.0, 1.0),
            ("ピザボックスXL(箱)", 0.0, 1.0), ("サイドボックスS(個)", 0.0, 25.0), ("サイドボックスM(個)", 0.0, 100.0),
            ("ピザ弁当(パック)", 0.0, 1.0), ("サラダ容器(パック)", 0.0, 1.0), ("サラダ蓋(パック)", 0.0, 1.0),
            ("サイド袋大(パック)", 0.0, 1.0), ("サイド袋小(パック)", 0.0, 1.0), ("クッキングシート(パック)", 0.0, 1.0),
            ("丸スプーン(本)", 0.0, 100.0), ("ディップ容器(個)", 0.0, 50.0), ("ディップ蓋(個)", 0.0, 50.0),
            ("フォーク(本)", 0.0, 100.0), ("S袋(パック)", 0.0, 4.0), ("ML袋(パック)", 0.0, 4.0),
            ("XL袋(パック)", 0.0, 1.0), ("スープカップ(パック)", 0.0, 1.0), ("カップリッド(パック)", 0.0, 1.0),
            ("シェイク用平蓋(パック)", 0.0, 1.0), ("ピザ置台(パック)", 0.0, 1.0), ("耐熱255ボル皿(パック)", 0.0, 1.0),
            ("耐熱255ぼる蓋(パック)", 0.0, 1.0), ("ストロー(本)", 0.0, 200.0), ("シェイクカップ420(パック)", 0.0, 1.0),
            ("シェイク用蓋(パック)", 0.0, 1.0), ("ベーキングカップ(パック)", 0.0, 1.0), ("サーマルロールレジロール(巻)", 0.0, 10.0)
        ]
        # PostgreSQLでは ? の代わりに %s を使います
        c.executemany("INSERT INTO inventory VALUES (%s, %s, %s)", default_items)
        
        default_presets = [
            ("水曜日", "S板(枚)", 60.0), ("水曜日", "L板(枚)", 80.0), ("水曜日", "M板(枚)", 70.0),
            ("水曜日", "チーズ(箱)", 13.0), ("水曜日", "トマソ(パック)", 7.0), ("水曜日", "バジソ(パック)", 7.0),
            ("水曜日", "燻ベーコン(パック)", 7.0), ("水曜日", "ハム(パック)", 3.0), ("水曜日", "イタソ(パック)", 7.0),
            ("水曜日", "ペパロニ(パック)", 8.0), ("水曜日", "コーン(缶)", 10.0), ("水曜日", "ハラピ(缶)", 7.0),
            ("水曜日", "コーングリッツ(KG)", 10.0), ("水曜日", "パイナップル(缶)", 8.0), ("水曜日", "スラポ(パック)", 9.0),
            ("水曜日", "マヨソース(本)", 8.0), ("水曜日", "カマソ(パック)", 10.0), ("水曜日", "パセリ(パック)", 1.0),
            ("水曜日", "アラソ(パック)", 8.0), ("水曜日", "ガーリック(パック)", 7.0), ("水曜日", "プラックペッパー(パック)", 1.0),
            ("水曜日", "ポッコン(袋)", 2.0), ("水曜日", "カマンベールチーズ固形(袋)", 3.0), ("水曜日", "オイル(本)", 1.0),
            ("水曜日", "カルビ(パック)", 7.0), ("水曜日", "ストチ(ホテルパン)", 1.0), ("水曜日", "チェリトマ(パック)", 20.0),
            ("水曜日", "バジル(パック)", 2.0), ("水曜日", "ビーフ(パック)", 7.0), ("水曜日", "BBQソース(パック)", 4.0),
            ("水曜日", "パルメザンチーズ(袋)", 2.0), ("水曜日", "ローチ(袋)", 10.0), ("水曜日", "イースト(パック)", 1.0),
            ("水曜日", "プレミックス(袋)", 10.0), ("水曜日", "チェダーソース(パック)", 7.0), ("水曜日", "大海老(パック)", 7.0),
            ("水曜日", "チキテリ(パック)", 10.0), ("水曜日", "コーラ15L(本)", 0.0), ("水曜日", "コーラゼロ15L(本)", 0.0),
            ("水曜日", "コーラ500(本)", 0.0), ("水曜日", "コーラゼロ500(本)", 0.0), ("水曜日", "クー(本)", 0.0),
            ("水曜日", "爽健美茶(本)", 0.0), ("水曜日", "ジンジャー(本)", 0.0), ("水曜日", "ドクペ(本)", 0.0),
            ("水曜日", "スプライト(本)", 0.0), ("水曜日", "パルメザン小袋(個)", 50.0), ("水曜日", "骨付き(パック)", 5.0),
            ("水曜日", "ポテトフライ(パック)", 10.0), ("水曜日", "ナゲット(パック)", 8.0), ("水曜日", "ナゲットソース(個)", 60.0),
            ("水曜日", "ケチャップ(個)", 80.0), ("水曜日", "タバスコ(本)", 4.0), ("水曜日", "シーザー(個)", 50.0),
            ("水曜日", "クルトン(個)", 50.0), ("水曜日", "カスパイ(個)", 30.0), ("水曜日", "粉糖(パック)", 1.0),
            ("水曜日", "サウザン(個)", 70.0), ("水曜日", "コンソメ(パック)", 1.0), ("水曜日", "チリガーリック(パック)", 1.0),
            ("水曜日", "コンポタ(個)", 14.0), ("水曜日", "くらむ(個)", 20.0), ("水曜日", "エッグタルト(個)", 80.0),
            ("水曜日", "からあげ(パック)", 7.0), ("水曜日", "ディップソース(本)", 3.0), ("水曜日", "アイス(箱)", 10.0),
            ("水曜日", "牛乳(パック)", 5.0), ("水曜日", "チョコソース(本)", 2.0), ("水曜日", "ホイップ(パック)", 8.0),
            ("水曜日", "フォンダン(パック)", 4.0), ("水曜日", "ストロベリー(パック)", 2.0), ("水曜日", "チーズ棒(箱)", 8.0),
            ("水曜日", "ザクチキ(パック)", 5.0), ("水曜日", "レッドブル(本)", 10.0), ("水曜日", "オニオン(パック)", 5.0),
            ("水曜日", "マッシュ(パック)", 4.0), ("水曜日", "サラダ(パック)", 20.0), ("水曜日", "ほうれん草(パック)", 4.0),
            ("水曜日", "ピーマン(パック)", 5.0),
            ("日曜日", "S板(枚)", 60.0), ("日曜日", "L板(枚)", 80.0), ("日曜日", "M板(枚)", 70.0),
            ("日曜日", "チーズ(箱)", 13.0), ("日曜日", "トマソ(パック)", 7.0), ("日曜日", "バジソ(パック)", 7.0),
            ("日曜日", "燻ベーコン(パック)", 7.0), ("日曜日", "ハム(パック)", 3.0), ("日曜日", "イタソ(パック)", 7.0),
            ("日曜日", "ペパロニ(パック)", 8.0), ("日曜日", "コーン(缶)", 10.0), ("日曜日", "ハラピ(缶)", 7.0),
            ("日曜日", "コーングリッツ(KG)", 10.0), ("日曜日", "パイナップル(缶)", 8.0), ("日曜日", "スラポ(パック)", 9.0),
            ("日曜日", "マヨソース(本)", 8.0), ("日曜日", "カマソ(パック)", 10.0), ("日曜日", "パセリ(パック)", 1.0),
            ("日曜日", "アラソ(パック)", 8.0), ("日曜日", "ガーリック(パック)", 7.0), ("日曜日", "プラックペッパー(パック)", 1.0),
            ("日曜日", "ポッコン(袋)", 2.0), ("日曜日", "カマンベールチーズ固形(袋)", 3.0), ("日曜日", "オイル(本)", 1.0),
            ("日曜日", "カルビ(パック)", 7.0), ("日曜日", "ストチ(ホテルパン)", 1.0), ("日曜日", "チェリトマ(パック)", 20.0),
            ("日曜日", "バジル(パック)", 2.0), ("日曜日", "ビーフ(パック)", 7.0), ("日曜日", "BBQソース(パック)", 4.0),
            ("日曜日", "パルメザンチーズ(袋)", 2.0), ("日曜日", "ローチ(袋)", 10.0), ("日曜日", "イースト(パック)", 1.0),
            ("日曜日", "プレミックス(袋)", 10.0), ("日曜日", "チェダーソース(パック)", 7.0), ("日曜日", "大海老(パック)", 7.0),
            ("日曜日", "チキテリ(パック)", 10.0), ("日曜日", "コーラ15L(本)", 18.0), ("日曜日", "コーラゼロ15L(本)", 12.0),
            ("日曜日", "コーラ500(本)", 24.0), ("日曜日", "コーラゼロ500(本)", 12.0), ("日曜日", "クー(本)", 12.0),
            ("日曜日", "爽健美茶(本)", 12.0), ("日曜日", "ジンジャー(本)", 12.0), ("日曜日", "ドクペ(本)", 12.0),
            ("日曜日", "スプライト(本)", 12.0), ("日曜日", "パルメザン小袋(個)", 50.0), ("日曜日", "骨付き(パック)", 5.0),
            ("日曜日", "ポテトフライ(パック)", 10.0), ("日曜日", "ナゲット(パック)", 8.0), ("日曜日", "ナゲットソース(個)", 60.0),
            ("日曜日", "ケチャップ(個)", 80.0), ("日曜日", "タバスコ(本)", 4.0), ("日曜日", "シーザー(個)", 50.0),
            ("日曜日", "クルトン(個)", 50.0), ("日曜日", "カスパイ(個)", 30.0), ("日曜日", "粉糖(パック)", 1.0),
            ("日曜日", "サウザン(個)", 70.0), ("日曜日", "コンソメ(パック)", 1.0), ("日曜日", "チリガーリック(パック)", 1.0),
            ("日曜日", "コンポタ(個)", 14.0), ("日曜日", "くらむ(個)", 20.0), ("日曜日", "エッグタルト(個)", 80.0),
            ("日曜日", "からあげ(パック)", 7.0), ("日曜日", "ディップソース(本)", 3.0), ("日曜日", "アイス(箱)", 10.0),
            ("日曜日", "牛乳(パック)", 5.0), ("日曜日", "チョコソース(本)", 2.0), ("日曜日", "ホイップ(パック)", 8.0),
            ("日曜日", "フォンダン(パック)", 4.0), ("日曜日", "ストロベリー(パック)", 2.0), ("日曜日", "チーズ棒(箱)", 8.0),
            ("日曜日", "ザクチキ(パック)", 5.0), ("日曜日", "レッドブル(本)", 10.0), ("日曜日", "オニオン(パック)", 5.0),
            ("日曜日", "マッシュ(パック)", 4.0), ("日曜日", "サラダ(パック)", 20.0), ("日曜日", "ほうれん草(パック)", 4.0),
            ("日曜日", "ピーマン(パック)", 5.0),
            ("日曜日", "ピザボックスS(箱)", 7.0), ("日曜日", "ピザボックスM(箱)", 10.0), ("日曜日", "ピザボックスL(箱)", 10.0),
            ("日曜日", "ピザボックスXL(箱)", 3.0), ("日曜日", "サイドボックスS(個)", 50.0), ("日曜日", "サイドボックスM(個)", 500.0),
            ("日曜日", "ピザ弁当(パック)", 2.0), ("日曜日", "サラダ容器(パック)", 2.0), ("日曜日", "サラダ蓋(パック)", 2.0),
            ("日曜日", "サイド袋大(パック)", 5.0), ("日曜日", "サイド袋小(パック)", 5.0), ("日曜日", "クッキングシート(パック)", 1.0),
            ("日曜日", "丸スプーン(本)", 50.0), ("日曜日", "ディップ容器(個)", 50.0), ("日曜日", "ディップ蓋(個)", 50.0),
            ("日曜日", "フォーク(本)", 40.0), ("日曜日", "S袋(パック)", 4.0), ("日曜日", "ML袋(パック)", 5.0),
            ("日曜日", "XL袋(パック)", 3.0), ("日曜日", "スープカップ(パック)", 2.0), ("日曜日", "カップリッド(パック)", 2.0),
            ("日曜日", "シェイク用平蓋(パック)", 1.0), ("日曜日", "ピザ置台(パック)", 3.0), ("日曜日", "耐熱255ボル皿(パック)", 1.0),
            ("日曜日", "耐熱255ぼる蓋(パック)", 1.0), ("日曜日", "ストロー(本)", 50.0), ("日曜日", "シェイクカップ420(パック)", 1.0),
            ("日曜日", "シェイク用蓋(パック)", 1.0), ("日曜日", "ベーキングカップ(パック)", 1.0), ("日曜日", "サーマルロールレジロール(巻)", 10.0)
        ]
        c.executemany("INSERT INTO presets VALUES (%s, %s, %s)", default_presets)
    conn.commit()
    conn.close()

def get_items():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_name, current_stock, lot_size FROM inventory")
    data = {row[0]: {"stock": row[1], "lot_size": row[2]} for row in c.fetchall()}
    conn.close()
    return data

def get_presets():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT preset_name, item_name, required_amount FROM presets")
    presets = {}
    for p_name, i_name, amount in c.fetchall():
        if p_name not in presets:
            presets[p_name] = {}
        presets[p_name][i_name] = amount
    conn.close()
    return presets

def save_inventory(item_name, stock):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE inventory SET current_stock = %s WHERE item_name = %s", (stock, item_name))
    conn.commit()
    conn.close()

def add_item_to_db(item_name, lot_size=1.0):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO inventory (item_name, current_stock, lot_size) VALUES (%s, 0.0, %s) ON CONFLICT (item_name) DO NOTHING", (item_name, lot_size))
    c.execute("SELECT DISTINCT preset_name FROM presets")
    for row in c.fetchall():
        c.execute("INSERT INTO presets (preset_name, item_name, required_amount) VALUES (%s, %s, 0.0) ON CONFLICT (preset_name, item_name) DO NOTHING", (row[0], item_name))
    conn.commit()
    conn.close()

def add_preset_to_db(preset_name):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_name FROM inventory")
    for row in c.fetchall():
        c.execute("INSERT INTO presets (preset_name, item_name, required_amount) VALUES (%s, %s, 0.0) ON CONFLICT (preset_name, item_name) DO NOTHING", (preset_name, row[0]))
    conn.commit()
    conn.close()

def update_preset_amount(preset_name, item_name, amount):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE presets SET required_amount = %s WHERE preset_name = %s AND item_name = %s", (amount, preset_name, item_name))
    conn.commit()
    conn.close()

# ==========================================
# 2. アプリのUIと操作ロジック
# ==========================================
def main(page: ft.Page):
    page.title = "在庫・発注管理アプリ"
    page.window_width = 450 
    page.window_height = 800
    init_db()

    main_tab_content = ft.Column(scroll="auto")
    settings_tab_content = ft.Column(scroll="auto")
    content_area = ft.Container(content=main_tab_content, expand=True, padding=10)

    def refresh_ui():
        main_tab_content.controls.clear()
        settings_tab_content.controls.clear()
        
        inventory_data = get_items()
        presets_data = get_presets()
        preset_names = list(presets_data.keys())
        item_names = list(inventory_data.keys())

        preset_dropdown = ft.Dropdown(
            label="発注基準のプリセット",
            options=[ft.dropdown.Option(key=k) for k in preset_names],
            value=preset_names[0] if preset_names else None,
        )
        
        inventory_inputs = {}
        item_rows = []
        for item, info in inventory_data.items():
            stock = info["stock"]
            inp = ft.TextField(
                value=str(stock), 
                keyboard_type="number", 
                width=90, 
                text_align="right"
            )
            inventory_inputs[item] = inp
            item_rows.append(
                ft.Row(
                    controls=[ft.Text(value=item, expand=True), inp], 
                    alignment="spaceBetween"
                )
            )

        result_view = ft.Column()

        def calculate(e):
            result_view.controls.clear()
            selected_p = preset_dropdown.value
            req_data = presets_data.get(selected_p, {})
            
            result_view.controls.append(ft.Text(value=f"【発注リスト: {selected_p}】", weight="bold"))

            for item in item_names:
                try:
                    stock = float(inventory_inputs[item].value)
                except:
                    stock = 0.0
                save_inventory(item, stock)
                
                req_stock = req_data.get(item, 0.0)
                lot_size = inventory_data[item]["lot_size"]
                deficit = req_stock - stock
                
                if deficit > 0:
                    if lot_size > 1.0:
                        order_units = math.ceil(deficit / lot_size)
                        result_view.controls.append(ft.Text(value=f"・{item}: {order_units} 発注 (不足{deficit} / 1ロット{lot_size}入)", color="red600"))
                    else:
                        order_amount = round(deficit, 1)
                        result_view.controls.append(ft.Text(value=f"・{item}: {order_amount} 発注 (目標{req_stock})", color="red600"))
                else:
                    result_view.controls.append(ft.Text(value=f"・{item}: 不要", color="green600"))
            
            page.snack_bar = ft.SnackBar(content=ft.Text(value="保存して計算しました"))
            page.snack_bar.open = True
            page.update()

        main_tab_content.controls.extend([
            preset_dropdown, 
            ft.Divider(), 
            *item_rows, 
            ft.Divider(),
            ft.Row(
                controls=[ft.FilledButton(content=ft.Text("保存して計算"), on_click=calculate)], 
                alignment="center"
            ),
            ft.Divider(), 
            result_view
        ])

        # 設定画面
        new_item_field = ft.TextField(label="新しい品名", expand=True)
        new_item_lot = ft.TextField(label="1発注の入数(通常1)", value="1", width=140)
        
        def on_add_item(e):
            if new_item_field.value:
                try:
                    lot = float(new_item_lot.value)
                except:
                    lot = 1.0
                add_item_to_db(new_item_field.value, lot)
                page.snack_bar = ft.SnackBar(content=ft.Text(value=f"{new_item_field.value}を追加しました"))
                page.snack_bar.open = True
                refresh_ui() 
        
        new_preset_field = ft.TextField(label="新しいプリセット名", expand=True)
        def on_add_preset(e):
            if new_preset_field.value:
                add_preset_to_db(new_preset_field.value)
                page.snack_bar = ft.SnackBar(content=ft.Text(value=f"{new_preset_field.value}を追加しました"))
                page.snack_bar.open = True
                refresh_ui()
                
        set_p_drop = ft.Dropdown(
            label="プリセット", 
            options=[ft.dropdown.Option(key=k) for k in preset_names], 
            value=preset_names[0] if preset_names else None, 
            expand=True
        )
        set_i_drop = ft.Dropdown(
            label="品物", 
            options=[ft.dropdown.Option(key=k) for k in item_names], 
            value=item_names[0] if item_names else None, 
            expand=True
        )
        set_amount = ft.TextField(label="必要数", keyboard_type="number", width=100)
        
        def on_update_amount(e):
            try:
                val = float(set_amount.value)
                update_preset_amount(set_p_drop.value, set_i_drop.value, val)
                page.snack_bar = ft.SnackBar(content=ft.Text(value="必要数を更新しました"))
                page.snack_bar.open = True
                refresh_ui()
            except ValueError:
                pass

        settings_tab_content.controls.extend([
            ft.Text(value="1. 新しい品物の追加", weight="bold"),
            ft.Row(controls=[new_item_field, new_item_lot, ft.FilledButton(content=ft.Text("追加"), on_click=on_add_item)]),
            ft.Divider(),
            ft.Text(value="2. 新しいプリセットの追加", weight="bold"),
            ft.Row(controls=[new_preset_field, ft.FilledButton(content=ft.Text("追加"), on_click=on_add_preset)]),
            ft.Divider(),
            ft.Text(value="3. プリセットごとの必要数設定", weight="bold"),
            ft.Row(controls=[set_p_drop, set_i_drop]),
            ft.Row(controls=[set_amount, ft.FilledButton(content=ft.Text("更新"), on_click=on_update_amount)]),
        ])

        page.update()

    def switch_tab(e):
        if e.control.selected_index == 0:
            content_area.content = main_tab_content
        else:
            content_area.content = settings_tab_content
        page.update()

    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(icon="list", label="発注・在庫"),
            ft.NavigationBarDestination(icon="settings", label="設定"),
        ],
        on_change=switch_tab
    )
    
    page.add(content_area)
    refresh_ui()

# クラウド（Render）およびローカルテスト両対応の起動設定
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    ft.run(main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=port)