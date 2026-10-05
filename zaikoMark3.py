import flet as ft
import psycopg2
import math
import os

# ==========================================
# 1. データベース設定と操作関数 
# ==========================================
# ★★★ 前回成功したURIをここに貼り付けてください ★★★
DB_URI = os.environ.get("DATABASE_URL", "postgresql://postgres.pixsxswdcaoggusfgbhv:Hionatamawari%402379070897@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres")

def get_conn():
    return psycopg2.connect(DB_URI)

def init_db():
    # クラウド側にデータは保存済みなので、ここではテーブルの確認だけ行います
    conn = get_conn()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (item_name TEXT PRIMARY KEY, current_stock REAL, lot_size REAL DEFAULT 1.0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS presets (preset_name TEXT, item_name TEXT, required_amount REAL, PRIMARY KEY(preset_name, item_name))''')
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

    main_tab_content = ft.Column(expand=True)
    settings_tab_content = ft.Column(scroll="auto", expand=True)
    content_area = ft.Container(content=main_tab_content, expand=True, padding=10)

    # 包材リスト（これらに合致するものは「包材」タブへ、それ以外は「食材」タブへ）
    packaging_list = [
        "ピザボックスS(箱)", "ピザボックスM(箱)", "ピザボックスL(箱)", "ピザボックスXL(箱)",
        "サイドボックスS(個)", "サイドボックスM(個)", "ピザ弁当(パック)", "サラダ容器(パック)",
        "サラダ蓋(パック)", "サイド袋大(パック)", "サイド袋小(パック)", "クッキングシート(パック)",
        "丸スプーン(本)", "ディップ容器(個)", "ディップ蓋(個)", "フォーク(本)", "S袋(パック)",
        "ML袋(パック)", "XL袋(パック)", "スープカップ(パック)", "カップリッド(パック)",
        "シェイク用平蓋(パック)", "ピザ置台(パック)", "耐熱255ボル皿(パック)", "耐熱255ぼる蓋(パック)",
        "ストロー(本)", "シェイクカップ420(パック)", "シェイク用蓋(パック)", "ベーキングカップ(パック)",
        "サーマルロールレジロール(巻)"
    ]

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
            expand=True
        )
        
        inventory_inputs = {}
        food_controls = []
        packaging_controls = []
        all_text_fields = []

        # 品物リストの構築
        for item in item_names:
            info = inventory_data.get(item, {"stock": 0.0, "lot_size": 1.0})
            stock = info["stock"]
            
            # 0の場合は空欄にして、タップ時の手間をなくす
            display_stock = "" if stock == 0 else (str(int(stock)) if stock.is_integer() else str(stock))
            
            inp = ft.TextField(
                value=display_stock, 
                hint_text="0",
                keyboard_type=ft.KeyboardType.NUMBER, 
                width=100, 
                text_align="right",
                content_padding=10 # スマホで押しやすくする
            )
            inventory_inputs[item] = inp
            all_text_fields.append(inp)
            
            row = ft.Row([ft.Text(value=item, expand=True, size=16), inp], alignment="spaceBetween")
            
            if item in packaging_list:
                packaging_controls.append(row)
            else:
                food_controls.append(row)

        num_food = len(food_controls)

        # エンターキーで次の入力欄へ移動する処理
        for i in range(len(all_text_fields)):
            def make_submit(index):
                def on_submit(e):
                    next_idx = index + 1
                    if next_idx < len(all_text_fields):
                        # 食材の最後まできたら、包材タブに自動で切り替える
                        if next_idx == num_food:
                            tabs.selected_index = 1
                            page.update()
                        all_text_fields[next_idx].focus()
                    else:
                        page.focus() # 最後の項目ならキーボードを閉じる
                return on_submit
            all_text_fields[i].on_submit = make_submit(i)

        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="食材", content=ft.ListView(controls=food_controls, expand=True, spacing=10, padding=10)),
                ft.Tab(text="包材", content=ft.ListView(controls=packaging_controls, expand=True, spacing=10, padding=10)),
            ],
            expand=True,
        )
        result_view = ft.Column()

        def calculate(e):
            result_view.controls.clear()
            selected_p = preset_dropdown.value
            req_data = presets_data.get(selected_p, {})
            
            order_text_lines = [f"【発注リスト: {selected_p}】"]

            for item in item_names:
                val = inventory_inputs[item].value
                stock = float(val) if val else 0.0 # 空欄の場合は0として計算
                save_inventory(item, stock)
                
                req_stock = req_data.get(item, 0.0)
                lot_size = inventory_data[item]["lot_size"]
                deficit = req_stock - stock
                
                # 不要なものは非表示にし、必要なものだけをリスト化する
                if deficit > 0:
                    if lot_size > 1.0:
                        order_units = math.ceil(deficit / lot_size)
                        line_text = f"・{item}: {order_units} 発注 (不足{deficit} / 1ロット{lot_size}入)"
                    else:
                        order_amount = int(deficit) if deficit.is_integer() else round(deficit, 1)
                        line_text = f"・{item}: {order_amount} 発注"
                        
                    result_view.controls.append(ft.Text(value=line_text, color="red600", size=16))
                    order_text_lines.append(line_text)
            
            if len(order_text_lines) == 1:
                result_view.controls.append(ft.Text(value="すべて在庫が足りています！発注不要です。", color="green600", size=16))

            def copy_to_clipboard(e):
                page.set_clipboard("\n".join(order_text_lines))
                page.snack_bar = ft.SnackBar(content=ft.Text("発注リストをコピーしました！LINE等に貼り付けできます。"))
                page.snack_bar.open = True
                page.update()

            if len(order_text_lines) > 1:
                result_view.controls.append(
                    ft.FilledButton(content=ft.Text("リストをコピーする", size=16), on_click=copy_to_clipboard, icon="copy")
                )
            
            page.snack_bar = ft.SnackBar(content=ft.Text("保存して計算しました"))
            page.snack_bar.open = True
            page.update()

        main_tab_content.controls.extend([
            ft.Row([preset_dropdown, ft.FilledButton(content=ft.Text("保存して計算"), on_click=calculate)]),
            tabs,
            ft.Divider(), 
            result_view
        ])

        # ====================
        # ② 設定画面
        # ====================
        new_item_field = ft.TextField(label="新しい品名", expand=True)
        new_item_lot = ft.TextField(label="1発注の入数(通常1)", value="1", width=140)
        
        def on_add_item(e):
            if new_item_field.value:
                try: lot = float(new_item_lot.value)
                except: lot = 1.0
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
                
        set_p_drop = ft.Dropdown(label="プリセット", options=[ft.dropdown.Option(key=k) for k in preset_names], value=preset_names[0] if preset_names else None, expand=True)
        set_i_drop = ft.Dropdown(label="品物", options=[ft.dropdown.Option(key=k) for k in item_names], value=item_names[0] if item_names else None, expand=True)
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    ft.run(main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=port)
