import random
import json
import os

USER_DATA_FILE = "users.json"

def wait_lines(*lines):
    for line in lines:
        print(line)
        input()

class Pet:
    def __init__(self, name, atk, max_hp, speed):
        self.name = name
        self.atk = atk
        self.max_hp = max_hp
        self.hp = max_hp
        self.speed = speed
        self.dodging = False
        self.charge_count = 0
        self.dodge_rate = 1.0
        self.sleeping = False
        self.angry = False
        self.is_bleeding = False

    def reset_state(self):
        self.dodging = False

def calculate_damage(attacker, defender):
    multiplier = 2 ** attacker.charge_count if attacker.charge_count > 0 else 1.0
    return int(attacker.atk * multiplier), multiplier

def show_hp_status(target):
    hp_percent = max(0, round(target.hp / target.max_hp * 100))
    wait_lines(f"🩸 {target.name} HP: {max(0, target.hp)} / {target.max_hp} ({hp_percent}%)")

def create_enemy(index):
    if index == 1:
        return Pet("Trainer Dummy", 30, 200, 30)
    elif index == 2:
        return Pet("GlassCannon", 5000, 10, 200)
    elif index == 3:
        lion = Pet("BleedingLion", 999, 999, 40)
        lion.is_bleeding = True
        return lion
    elif index == 4:
        tiger = Pet("SleepingTiger", 999, 1000, 40)
        tiger.sleeping = True
        tiger.angry = False
        return tiger

def try_hide(player):
    return True

def battle(player, enemy):
    wait_lines(f"➡️ Battle Start! {player.name} vs {enemy.name}")
    if player.speed >= enemy.speed:
        wait_lines(f"{player.name} is faster and will act first.")
        turn = "player"
    else:
        wait_lines(f"{enemy.name} is faster and will act first.")
        turn = "enemy"
    while player.hp > 0 and enemy.hp > 0:
        if turn == "player":
            action = input("Choose action (attack / charge / dodge): ").strip().lower()
            while action not in ("attack", "charge", "dodge"):
                action = input("Please choose a valid action (attack / charge / dodge): ").strip().lower()
            if action == "attack":
                dmg, multiplier = calculate_damage(player, enemy)
                enemy.hp -= dmg
                wait_lines(f"⚔️ Dealt {dmg} damage{' with charged attack!' if multiplier > 1.0 else ''} (x{multiplier:.1f})")
                show_hp_status(enemy)
                player.charge_count = 0

                if hasattr(enemy, 'sleeping') and enemy.sleeping:
                    wait_lines("😠 The SleepingTiger wakes up and becomes furious!")
                    enemy.sleeping = False
                    enemy.angry = True

            elif action == "charge":
                if player.charge_count >= 6:
                    wait_lines("⚠️ Maximum charge reached (x64)!")
                else:
                    player.charge_count += 1
                    wait_lines(f"⚡ Charging energy! Your next attack will deal x{2 ** player.charge_count:.1f} damage.")

            elif action == "dodge":
                player.dodging = True
                wait_lines("🌀 You will attempt to dodge the next attack.")
            turn = "enemy"

        else:
            if hasattr(enemy, 'sleeping') and enemy.sleeping:
                wait_lines("😴 SleepingTiger is resting and does not attack.")
            else:
                if player.dodging:
                    if random.random() < player.dodge_rate:
                        wait_lines("✔️ You dodged the enemy attack!")
                        player.reset_state()
                        turn = "player"
                        continue
                    else:
                        wait_lines("❌ Dodge failed!")
                dmg, _ = calculate_damage(enemy, player)
                player.hp -= dmg
                wait_lines(f"💥 {enemy.name} deals {dmg} damage!")
                show_hp_status(player)

            player.reset_state()
            turn = "player"

        if enemy.is_bleeding and enemy.hp > 0:
            bleed = max(1, enemy.max_hp // 6)
            enemy.hp -= bleed
            wait_lines(f"🩸 {enemy.name} is bleeding and loses {bleed} HP!")
            show_hp_status(enemy)

    return player.hp > 0

def allocate_stats():
    total = 500
    stats = {}
    for attr in ["atk", "hp", "speed"]:
        while True:
            try:
                val = int(input(f"Assign points to {attr} (remaining: {total}): "))
                if 0 <= val <= total:
                    stats[attr] = val
                    total -= val
                    break
                else:
                    print("❗ Invalid number.")
            except:
                print("❗ Enter a valid integer.")
    return stats

def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f)

def login_flow():
    users = load_users()
    while True:
        action = input("Register or Login? ").lower()
        if action == "register":
            while True:
                username = input("Enter username: ")
                if not username.isalnum() or len(username) > 16:
                    print("Invalid username. Use letters/numbers only, max 16 chars.")
                    continue
                if username in users:
                    print("Username already exists.")
                    continue
                pw1 = input("Enter password: ")
                pw2 = input("Confirm password: ")
                if pw1 != pw2 or not any(c.isalpha() for c in pw1) or not any(c.isdigit() for c in pw1):
                    print("Passwords must match and contain letters and numbers.")
                    continue
                users[username] = {"password": pw1}
                save_users(users)
                print("Registration successful!")
                return
        elif action == "login":
            username = input("Username: ")
            pw = input("Password: ")
            if users.get(username, {}).get("password") == pw:
                print("Login successful!")
                return
            else:
                print("Invalid credentials.")

def game():
    login_flow()
    wait_lines("Your friend is severely injured.",
               "Only a rare herb deep in the forest can save them.",
               "You must venture into the wild with your pet companion.")
    name = input("Name your pet: ")
    stats = allocate_stats()
    player_pet = Pet(name, stats['atk'], stats['hp'], stats['speed'])
    enemies_killed = 0
    hid_all = True
    for i in range(1, 5):
        enemy = create_enemy(i)
        stage_msg = {
            1: ["You encounter a training dummy..."],
            2: ["A glass cannon appears!"],
            3: ["A wounded lion blocks your path. It bleeds steadily but still stands strong."],
            4: ["The final guardian—SleepingTiger—blocks the path. It shows no signs of aggression unless disturbed..."]
        }
        wait_lines(*stage_msg[i])
        while True:
            choice = input("Fight or hide? ").strip().lower()
            if choice == "hide":
                wait_lines("✔️ Successfully hid!")
                break
            elif choice == "fight":
                hid_all = False
                survived = battle(player_pet, enemy)
            else:
                print("Please enter 'fight' or 'hide'")
                continue
            if survived:
                if i != 1:
                    enemies_killed += 1
                break
            else:
                wait_lines("🔁 Reallocate your stats and try again!")
                stats = allocate_stats()
                player_pet = Pet(name, stats['atk'], stats['hp'], stats['speed'])

    wait_lines("🌿 You retrieved the forest herb!")
    if hid_all:
        wait_lines("🌸 Hidden Ending: Forest Guardian – You avoided all conflict.")
        wait_lines("✨ Peacekeeper Ending: You harmed no one to save your friend!(Except poor trainer dummy...)")
    else:
        wait_lines("⚠️ Took Lives to Save One Ending: You succeeded, but at what cost?")

if __name__ == "__main__":
    game()
