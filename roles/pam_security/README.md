# Ansible Role: pam_security

Configure Touch ID and YubiKey hardware authentication for sudo on macOS.

## Features

- **Touch ID for sudo** - Use Touch ID/Face ID instead of typing password
- **YubiKey support** - Hardware authentication with YubiKey (U2F)
- **Safe configuration** - Backs up original PAM files before modification
- **Flexible modes** - Configure authentication as required, sufficient, or optional

## Requirements

- macOS with Touch ID (MacBook Pro with Touch Bar, M1/M2/M3 Macs)
- For YubiKey: `pam-u2f` installed via Homebrew
- Root/sudo access to modify `/etc/pam.d/sudo`

## Role Variables

### Touch ID Settings

```yaml
# Enable Touch ID for sudo
pam_touchid_enabled: true

# Backup original PAM configuration
pam_backup_original: true
pam_backup_dir: /etc/pam.d/backups
```

### YubiKey Settings

```yaml
# Enable YubiKey authentication
pam_yubikey_enabled: false

# Install pam-u2f via Homebrew
pam_yubikey_install_module: true

# Authentication mode
pam_yubikey_mode: sufficient  # required, sufficient, optional

# U2F keys file location
pam_u2f_authfile: "{{ ansible_env.HOME }}/.config/Yubico/u2f_keys"
```

## Dependencies

- `homebrew` role (when installing pam-u2f)

## Example Playbook

### Touch ID Only (Recommended)

```yaml
---
- name: Enable Touch ID for sudo
  hosts: localhost
  become: true
  roles:
    - role: pam_security
      vars:
        pam_touchid_enabled: true
        pam_yubikey_enabled: false
```

### Touch ID + YubiKey

```yaml
---
- name: Enable Touch ID and YubiKey
  hosts: localhost
  become: true
  roles:
    - role: pam_security
      vars:
        pam_touchid_enabled: true
        pam_yubikey_enabled: true
        pam_yubikey_mode: sufficient
```

### YubiKey Required (No Password Fallback)

```yaml
---
- name: Require YubiKey for sudo
  hosts: localhost
  become: true
  roles:
    - role: pam_security
      vars:
        pam_touchid_enabled: false
        pam_yubikey_enabled: true
        pam_yubikey_mode: required
```

## Public Functions

### configure_touchid

Configure Touch ID only.

```yaml
- name: Enable Touch ID
  ansible.builtin.import_role:
    name: pam_security
    tasks_from: configure_touchid
  vars:
    pam_touchid_enabled: true
```

### configure_yubikey

Configure YubiKey only.

```yaml
- name: Enable YubiKey
  ansible.builtin.import_role:
    name: pam_security
    tasks_from: configure_yubikey
  vars:
    pam_yubikey_enabled: true
    pam_yubikey_mode: sufficient
```

## YubiKey Setup Instructions

After enabling YubiKey support, you must register your keys:

### Register Your First YubiKey

```bash
# Create config directory
mkdir -p ~/.config/Yubico

# Insert YubiKey and register it
pamu2fcfg > ~/.config/Yubico/u2f_keys

# Touch YubiKey when it blinks
```

### Register Additional YubiKeys

```bash
# Insert second YubiKey
pamu2fcfg -n >> ~/.config/Yubico/u2f_keys

# Touch YubiKey when it blinks
```

### Test YubiKey Authentication

```bash
# Clear sudo cache
sudo -k

# Test sudo with YubiKey
sudo ls

# Touch YubiKey or use Touch ID (depending on mode)
```

## Authentication Modes

### Sufficient (Default, Recommended)

Touch ID or YubiKey can authenticate alone, OR fall through to password.

- Try Touch ID first
- If no Touch ID, try YubiKey
- If no YubiKey, fall through to password

### Required

YubiKey MUST be present and valid. No password fallback.

⚠️ **Warning**: If you lose your YubiKey, you cannot sudo! Use with caution.

### Optional

YubiKey is checked but not required. Always falls through to password.

Less secure - mainly for testing.

## Testing

### Test Touch ID

```bash
# Clear sudo authentication cache
sudo -k

# Run sudo command
sudo ls

# You should see Touch ID prompt instead of password prompt
```

### Test YubiKey

```bash
# Clear sudo cache
sudo -k

# Run sudo command
sudo ls

# Touch your YubiKey when it blinks
```

## Troubleshooting

### Touch ID Not Working

1. **Verify configuration**:
   ```bash
   cat /etc/pam.d/sudo | grep pam_tid.so
   ```
   Should show: `auth       sufficient     pam_tid.so`

2. **Check macOS version**:
   Touch ID for sudo requires macOS 10.12.2+

3. **Restart terminal**:
   Open a new terminal window after configuration

### YubiKey Not Working

1. **Verify pam-u2f installed**:
   ```bash
   which pamu2fcfg
   ```

2. **Check registration file**:
   ```bash
   cat ~/.config/Yubico/u2f_keys
   ```
   Should contain YubiKey registration data

3. **Re-register YubiKey**:
   ```bash
   pamu2fcfg > ~/.config/Yubico/u2f_keys
   ```

### Locked Out of Sudo

If configuration breaks sudo access:

1. **Reboot into Recovery Mode** (Cmd+R during startup)
2. **Open Terminal** from Utilities menu
3. **Restore backup**:
   ```bash
   cp /Volumes/Macintosh\ HD/etc/pam.d/backups/sudo.* /Volumes/Macintosh\ HD/etc/pam.d/sudo
   ```
4. **Reboot normally**

## Security Considerations

- **Touch ID** - Convenient and secure for single-user Macs
- **YubiKey Required Mode** - Most secure, but risky if YubiKey is lost
- **YubiKey Sufficient Mode** - Balanced security with password fallback
- **Backups** - Always keep PAM backups in case of configuration issues
- **Multiple YubiKeys** - Register backup YubiKeys to avoid lockout

## Tags

- `pam_security` - All tasks
- `pam_security:validate` - Validation only
- `pam_security:touchid` - Touch ID configuration
- `pam_security:yubikey` - YubiKey configuration
- `pam_security:summary` - Display summary

## Notes

- Requires `become: true` (root access)
- Changes take effect immediately (no restart needed)
- Original PAM config backed up to `/etc/pam.d/backups/`
- Safe to run multiple times (idempotent)

## License

MIT

## Author

Brian Grimmett
