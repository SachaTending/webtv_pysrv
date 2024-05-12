from base64 import b64decode
from Cryptodome.Cipher import DES, ARC4
from Cryptodome.Hash import MD5
from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.Padding import pad, unpad
import base64

#d = b64decode(b"vr+Z6SoHJNAwTcVjsIsZWw275MmPZ5N+CJFso0qMpBDu0SDl8koBVwp0HdK+B3AHBpTk1gjaqppJHUvo7eJmI5u+dLYug0+v2ox3WYyYvTFuP4FqgbBnmy39ePHaO6fWxxO8XudOtHOB0qO0")

DES_ENC = DES.MODE_ECB

class WTVNetworkSecurity():
	initial_shared_key = b''
	current_shared_key = b''
	incarnation = 1
	session_key1 = b''
	session_key2 = b''
	hRC4_Key1 = None
	hRC4_Key2 = None

	def __init__(self, wtv_initial_key, wtv_incarnation = 1):
		initial_key = base64.b64decode(wtv_initial_key)

		if len(initial_key) == 8:
			self.incarnation = wtv_incarnation
			self.initial_shared_key =  initial_key
			self.current_shared_key = initial_key
		else:
			raise Exception("Invalid initial key length")

	def set_incarnation(self, wtv_incarnation):
		self.incarnation = wtv_incarnation

	def increment_incarnation(self):
		self.incarnation = self.incarnation + 1

	"""
	ROM:8049A310 Network__ProcessChallenge:               # CODE XREF: Network__SetHeader+210↓p
	ROM:8049A310
	ROM:8049A310 var_E8          = -0xE8
	ROM:8049A310 var_E0          = -0xE0
	ROM:8049A310 var_60          = -0x60
	ROM:8049A310 var_50          = -0x50
	ROM:8049A310 var_40          = -0x40
	ROM:8049A310 var_38          = -0x38
	ROM:8049A310 var_34          = -0x34
	ROM:8049A310 var_30          = -0x30
	ROM:8049A310 var_28          = -0x28
	ROM:8049A310 var_24          = -0x24
	ROM:8049A310 var_20          = -0x20
	ROM:8049A310 var_1C          = -0x1C
	ROM:8049A310 var_18          = -0x18
	ROM:8049A310 var_14          = -0x14
	ROM:8049A310 var_10          = -0x10
	ROM:8049A310 var_C           = -0xC
	ROM:8049A310 var_8           = -8
	ROM:8049A310 var_4           = -4
	ROM:8049A310 arg_42          =  0x42
	ROM:8049A310 arg_43          =  0x43
	ROM:8049A310
	ROM:8049A310                 addiu   $sp, -0xF8
	ROM:8049A314                 sw      $fp, 0xF8+var_8($sp)
	ROM:8049A318                 sw      $s3, 0xF8+var_1C($sp)
	ROM:8049A31C                 sw      $s2, 0xF8+var_20($sp)
	ROM:8049A320                 sw      $s1, 0xF8+var_24($sp)
	ROM:8049A324                 sw      $s0, 0xF8+var_28($sp)
	ROM:8049A328                 sw      $ra, 0xF8+var_4($sp)
	ROM:8049A32C                 sw      $s7, 0xF8+var_C($sp)
	ROM:8049A330                 sw      $s6, 0xF8+var_10($sp)
	ROM:8049A334                 sw      $s5, 0xF8+var_14($sp)
	ROM:8049A338                 sw      $s4, 0xF8+var_18($sp)
	ROM:8049A33C                 move    $fp, $a0
	ROM:8049A340                 move    $s0, $a1
	ROM:8049A344                 sw      $zero, 0xF8+var_30($sp)
	ROM:8049A348                 move    $s2, $zero
	ROM:8049A34C                 move    $s3, $zero
	ROM:8049A350                 bnez    $s0, loc_8049A364
	ROM:8049A354                 move    $s1, $zero
	ROM:8049A358                 break   0
	ROM:8049A35C                 j       loc_8049A5CC
	ROM:8049A360                 li      $v0, 0xFFFFFFFF
	ROM:8049A364  # ---------------------------------------------------------------------------
	ROM:8049A364
	ROM:8049A364 loc_8049A364:                            # CODE XREF: Network__ProcessChallenge+40↑j
	ROM:8049A364                 lbu     $v0, 0xF8+arg_42($fp)
	ROM:8049A368                 bnez    $v0, loc_8049A37C
	ROM:8049A36C                 addiu   $a0, $sp, 0xF8+var_E0
	ROM:8049A370                 break   0
	ROM:8049A374                 j       loc_8049A5CC
	ROM:8049A378                 li      $v0, 0xFFFFFFE9
	ROM:8049A37C  # ---------------------------------------------------------------------------
	ROM:8049A37C
	ROM:8049A37C loc_8049A37C:                            # CODE XREF: Network__ProcessChallenge+58↑j
	ROM:8049A37C                 move    $a1, $zero
	ROM:8049A380                 jal     wtv_memset
	ROM:8049A384                 li      $a2, 0xA4
	ROM:8049A388                 jal     wtv_strlen
	ROM:8049A38C                 move    $a0, $s0
	ROM:8049A390                 sw      $v0, 0xF8+var_38($sp)
	ROM:8049A394                 move    $a0, $s0
	ROM:8049A398                 jal     FNewFromBase64
	ROM:8049A39C                 addiu   $a1, $sp, 0xF8+var_38
	ROM:8049A3A0                 move    $s7, $v0
	ROM:8049A3A4                 beqz    $s7, loc_8049A578
	ROM:8049A3A8                 lui     $a0, 0x806D
	ROM:8049A3AC                 jal     AllocateMemorySystem
	ROM:8049A3B0                 lw      $a0, 0xF8+var_38($sp)
	ROM:8049A3B4                 move    $s2, $v0
	ROM:8049A3B8                 beqz    $s2, loc_8049A574
	ROM:8049A3BC                 move    $a0, $s2
	ROM:8049A3C0                 move    $a1, $s7
	ROM:8049A3C4                 jal     wtv_memcpy
	ROM:8049A3C8                 li      $a2, 8
	ROM:8049A3CC                 lui     $t0, 0x8000
	ROM:8049A3D0                 addiu   $s6, $fp, 0xF8+var_40
	ROM:8049A3D4                 addiu   $v0, $s2, 8
	ROM:8049A3D8                 lw      $a1, 0x8000587C
	ROM:8049A3DC                 move    $s4, $v0
	ROM:8049A3E0                 addiu   $a0, $sp, 0xF8+var_E0
	ROM:8049A3E4                 move    $a2, $s6
	ROM:8049A3E8                 jal     EVP_DecryptInit
	ROM:8049A3EC                 move    $a3, $zero
	ROM:8049A3F0                 lw      $v0, 0xF8+var_38($sp)
	ROM:8049A3F4                 addiu   $s5, $sp, 0xF8+var_34
	ROM:8049A3F8                 addiu   $v0, -8
	ROM:8049A3FC                 addiu   $a0, $sp, 0xF8+var_E0
	ROM:8049A400                 sw      $v0, 0xF8+var_E8($sp)
	ROM:8049A404                 move    $a1, $s4
	ROM:8049A408                 move    $a2, $s5
	ROM:8049A40C                 jal     EVP_DecryptUpdate
	ROM:8049A410                 addiu   $a3, $s7, 8
	ROM:8049A414                 lw      $s0, 0xF8+var_34($sp)
	ROM:8049A418                 addiu   $a0, $sp, 0xF8+var_E0
	ROM:8049A41C                 addu    $a1, $s4, $s0
	ROM:8049A420                 jal     EVP_DecryptFinal
	ROM:8049A424                 move    $a2, $s5
	ROM:8049A428                 lw      $v0, 0xF8+var_34($sp)
	ROM:8049A42C                 li      $v1, 0x60
	ROM:8049A430                 addu    $s0, $v0
	ROM:8049A434                 bne     $s0, $v1, loc_8049A578
	ROM:8049A438                 lui     $a0, 0x806D
	ROM:8049A43C                 move    $a0, $s4
	ROM:8049A440                 li      $a1, 0x50
	ROM:8049A444                 jal     MD5
	ROM:8049A448                 move    $a2, $zero
	ROM:8049A44C                 move    $a0, $v0
	ROM:8049A450                 addiu   $a1, $s2, 0x58
	ROM:8049A454                 jal     wtv_memcmp
	ROM:8049A458                 li      $a2, 0x10
	ROM:8049A45C                 beqz    $v0, loc_8049A46C
	ROM:8049A460                 li      $t0, 0xFFFFFFE9
	ROM:8049A464                 j       loc_8049A588
	ROM:8049A468                 sw      $t0, 0xF8+var_30($sp)
	ROM:8049A46C  # ---------------------------------------------------------------------------
	ROM:8049A46C
	ROM:8049A46C loc_8049A46C:                            # CODE XREF: Network__ProcessChallenge+14C↑j
	ROM:8049A46C                 addiu   $a0, $fp, 0xF8+var_60 ; ERIC: referenced in 80497AEC:Network__GetSessionKey1 (var_60=0x60, 0xF8 - 0x60 = 0x98)
	ROM:8049A470                 addiu   $a1, $s2, 0x30
	ROM:8049A474                 jal     wtv_memcpy
	ROM:8049A478                 li      $a2, 0x10
	ROM:8049A47C                 addiu   $a0, $fp, 0xF8+var_50 ; ERIC: referenced in 80497B60:Network__GetSessionKey2 (var_50=0x50, 0xF8 - 0x50 = 0xa8)
	ROM:8049A480                 addiu   $a1, $s2, 0x40
	ROM:8049A484                 jal     wtv_memcpy
	ROM:8049A488                 li      $a2, 0x10
	ROM:8049A48C                 move    $a0, $s6
	ROM:8049A490                 addiu   $a1, $s2, 0x50
	ROM:8049A494                 jal     wtv_memcpy
	ROM:8049A498                 li      $a2, 8
	ROM:8049A49C                 li      $v0, 1
	ROM:8049A4A0                 sb      $v0, 0xF8+arg_43($fp)
	ROM:8049A4A4                 sb      $v0, 0xF8+arg_42($fp)
	ROM:8049A4A8                 jal     AllocateMemorySystem
	ROM:8049A4AC                 li      $a0, 0x48
	ROM:8049A4B0                 move    $s3, $v0
	ROM:8049A4B4                 beqz    $s3, loc_8049A574
	ROM:8049A4B8                 move    $a0, $s3
	ROM:8049A4BC                 move    $a1, $s2
	ROM:8049A4C0                 jal     wtv_memcpy
	ROM:8049A4C4                 li      $a2, 8
	ROM:8049A4C8                 addiu   $a0, $s3, 0x18
	ROM:8049A4CC                 move    $a1, $s4
	ROM:8049A4D0                 li      $a2, 0x28
	ROM:8049A4D4                 jal     wtv_memcpy
	ROM:8049A4D8                 addiu   $s1, $s3, 8
	ROM:8049A4DC                 move    $a2, $s1
	ROM:8049A4E0                 move    $a0, $s4
	ROM:8049A4E4                 jal     MD5
	ROM:8049A4E8                 li      $a1, 0x28
	ROM:8049A4EC                 addiu   $a0, $sp, 0xF8+var_E0
	ROM:8049A4F0                 move    $a1, $zero
	ROM:8049A4F4                 jal     wtv_memset
	ROM:8049A4F8                 li      $a2, 0xA4
	ROM:8049A4FC                 lui     $t0, 0x8000
	ROM:8049A500                 lw      $a1, 0x8000587C
	ROM:8049A504                 move    $a2, $s6
	ROM:8049A508                 addiu   $a0, $sp, 0xF8+var_E0
	ROM:8049A50C                 jal     EVP_EncryptInit
	ROM:8049A510                 move    $a3, $zero
	ROM:8049A514                 li      $v0, 0x38
	ROM:8049A518                 move    $a1, $s1
	ROM:8049A51C                 move    $a3, $s1
	ROM:8049A520                 sw      $v0, 0xF8+var_E8($sp)
	ROM:8049A524                 addiu   $a0, $sp, 0xF8+var_E0
	ROM:8049A528                 jal     EVP_EncryptUpdate
	ROM:8049A52C                 move    $a2, $s5
	ROM:8049A530                 lw      $s0, 0xF8+var_34($sp)
	ROM:8049A534                 move    $a2, $s5
	ROM:8049A538                 addu    $a1, $s1, $s0
	ROM:8049A53C                 addiu   $s0, 8
	ROM:8049A540                 jal     EVP_EncryptFinal
	ROM:8049A544                 addiu   $a0, $sp, 0xF8+var_E0
	ROM:8049A548                 lw      $a1, 0xF8+var_34($sp)
	ROM:8049A54C                 move    $a0, $s3
	ROM:8049A550                 jal     FNewBase64StringFromBuf
	ROM:8049A554                 addu    $a1, $s0, $a1
	ROM:8049A558                 move    $s1, $v0
	ROM:8049A55C                 beqz    $s1, loc_8049A574
	ROM:8049A560                 move    $a0, $fp
	ROM:8049A564                 jal     Network__SetResponse
	ROM:8049A568                 move    $a1, $s1
	ROM:8049A56C                 j       loc_8049A588
	ROM:8049A570                 nop
	ROM:8049A574  # ---------------------------------------------------------------------------
	ROM:8049A574
	ROM:8049A574 loc_8049A574:                            # CODE XREF: Network__ProcessChallenge+A8↑j
	ROM:8049A574                                          # Network__ProcessChallenge+1A4↑j ...
	ROM:8049A574                 lui     $a0, 0x806D
	ROM:8049A578
	ROM:8049A578 loc_8049A578:                            # CODE XREF: Network__ProcessChallenge+94↑j
	ROM:8049A578                                          # Network__ProcessChallenge+124↑j
	ROM:8049A578                 li      $t0, 0xFFFFFFFF
	ROM:8049A57C                 addiu   $a0, (aProcesschallen - 0x806D0000)  # "ProcessChallenge Error"
	ROM:8049A580                 jal     DoMessage
	ROM:8049A584                 sw      $t0, 0xF8+var_30($sp)
	ROM:8049A588
	ROM:8049A588 loc_8049A588:                            # CODE XREF: Network__ProcessChallenge+154↑j
	ROM:8049A588                                          # Network__ProcessChallenge+25C↑j
	ROM:8049A588                 beqz    $s3, loc_8049A598
	ROM:8049A58C                 nop
	ROM:8049A590                 jal     FreeMemorySystem
	ROM:8049A594                 move    $a0, $s3
	ROM:8049A598
	ROM:8049A598 loc_8049A598:                            # CODE XREF: Network__ProcessChallenge:loc_8049A588↑j
	ROM:8049A598                 beqz    $s7, loc_8049A5A8
	ROM:8049A59C                 nop
	ROM:8049A5A0                 jal     FreeMemorySystem
	ROM:8049A5A4                 move    $a0, $s7
	ROM:8049A5A8
	ROM:8049A5A8 loc_8049A5A8:                            # CODE XREF: Network__ProcessChallenge:loc_8049A598↑j
	ROM:8049A5A8                 beqz    $s2, loc_8049A5B8
	ROM:8049A5AC                 nop
	ROM:8049A5B0                 jal     FreeMemorySystem
	ROM:8049A5B4                 move    $a0, $s2
	ROM:8049A5B8
	ROM:8049A5B8 loc_8049A5B8:                            # CODE XREF: Network__ProcessChallenge:loc_8049A5A8↑j
	ROM:8049A5B8                 beqz    $s1, loc_8049A5CC
	ROM:8049A5BC                 lw      $v0, 0xF8+var_30($sp)
	ROM:8049A5C0                 jal     FreeMemorySystem
	ROM:8049A5C4                 move    $a0, $s1
	ROM:8049A5C8                 lw      $v0, 0xF8+var_30($sp)
	ROM:8049A5CC
	ROM:8049A5CC loc_8049A5CC:                            # CODE XREF: Network__ProcessChallenge+4C↑j
	ROM:8049A5CC                                          # Network__ProcessChallenge+64↑j ...
	ROM:8049A5CC                 lw      $ra, 0xF8+var_4($sp)
	ROM:8049A5D0                 lw      $fp, 0xF8+var_8($sp)
	ROM:8049A5D4                 lw      $s7, 0xF8+var_C($sp)
	ROM:8049A5D8                 lw      $s6, 0xF8+var_10($sp)
	ROM:8049A5DC                 lw      $s5, 0xF8+var_14($sp)
	ROM:8049A5E0                 lw      $s4, 0xF8+var_18($sp)
	ROM:8049A5E4                 lw      $s3, 0xF8+var_1C($sp)
	ROM:8049A5E8                 lw      $s2, 0xF8+var_20($sp)
	ROM:8049A5EC                 lw      $s1, 0xF8+var_24($sp)
	ROM:8049A5F0                 lw      $s0, 0xF8+var_28($sp)
	ROM:8049A5F4                 jr      $ra
	ROM:8049A5F8                 addiu   $sp, 0xF8
	ROM:8049A5F8  # End of function Network__ProcessChallenge
	"""
	def ProcessChallenge(self, wtv_challenge):
		challenge = base64.b64decode(wtv_challenge)

		if len(challenge) > 8:
			hDES1 = DES.new(self.current_shared_key, DES_ENC)
			challenge_padded = pad(challenge[8:], 8)
			#challenge_padded = challenge[8:]
			#print(challenge)
			challenge_decrypted = hDES1.decrypt(challenge_padded)

			hMD5 = MD5.new()
			hMD5.update(challenge_decrypted[0:80])

			#if challenge_decrypted[80:96] == hMD5.digest():
			if True:
				self.current_shared_key = challenge_decrypted[72:80]

				challenge_echo = challenge_decrypted[0:40]
				hMD5 = MD5.new()
				hMD5.update(challenge_echo)
				challenge_echo_md5 = hMD5.digest()

				# RC4 encryption keys.  Stored in the wtv-ticket on the server side.
				self.session_key1 = challenge_decrypted[40:56]
				self.session_key2 = challenge_decrypted[56:72]

				hDES2 = DES.new(self.current_shared_key, DES.MODE_ECB)
				echo_encrypted = hDES2.encrypt(challenge_echo_md5 + challenge_echo)

				# Last bytes is just extra padding
				challenge_response = challenge[0:8] + echo_encrypted + (b'\x00' * 8)


				return str(base64.b64encode(challenge_response), "ascii")
			else:
				raise Exception("Couldn't solve challenge")

			return ""
		else:
			raise Exception("Invalid challenge length")

	def IssueChallenge(self):
		# bytes 0-8: Random id?  Just echoed in the response
		# bytes 8-XX: DES encrypted block.  Encrypted with the initial key or subsequent keys from the challenge.
		#	bytes 8-48: hidden random data we echo back in the response
		#	bytes 48-64: session key 1 used in RC4 encryption triggered by SECURE ON
		#	bytes 64-80: session key 2 used in RC4 encryption triggered by SECURE ON
		#	bytes 80-88: new key for future challenges
		#	bytes 88-104: MD5 of 8-88
		#	bytes 104-112: padding. not important

		random_id_question_mark = get_random_bytes(8)

		echo_me = get_random_bytes(40)
		self.session_key1 = get_random_bytes(16)
		self.session_key2 = get_random_bytes(16)
		new_shared_key = self.current_shared_key

		challenge_puzzle = echo_me + self.session_key1 + self.session_key2 + new_shared_key
		hMD5 = MD5.new()
		hMD5.update(challenge_puzzle)
		challenge_puzzle_md5 = hMD5.digest()

		challenge_secret = challenge_puzzle + challenge_puzzle_md5 + (b'\x00' * 8)

		# Shhhh!!
		hDES2 = DES.new(self.current_shared_key, DES_ENC)
		challenge_secreted = hDES2.encrypt(challenge_secret)

		self.current_shared_key = new_shared_key

		challenge = random_id_question_mark + challenge_secreted

		return str(base64.b64encode(challenge), "ascii")

	"""
	ROM:804A703C WTVProtocol__SetSessionKeys:             # CODE XREF: WTVProtocol__IdleSecureEnd+E4↑p
	ROM:804A703C                                          # WTVProtocol__GetSessionKeys+28↓p
	ROM:804A703C
	ROM:804A703C var_10          = -0x10
	ROM:804A703C var_C           = -0xC
	ROM:804A703C var_8           = -8
	ROM:804A703C
	ROM:804A703C                 addiu   $sp, -0x20
	ROM:804A7040                 sw      $s1, 0x20+var_C($sp)
	ROM:804A7044                 sw      $s0, 0x20+var_10($sp)
	ROM:804A7048                 move    $s0, $a0
	ROM:804A704C                 lui     $s1, 0x8000
	ROM:804A7050                 sw      $ra, 0x20+var_8($sp)
	ROM:804A7054                 lw      $a0, 0x80001274
	ROM:804A7058                 jal     Network__GetSessionKey1
	ROM:804A705C                 lw      $a1, 0x24($s0)
	ROM:804A7060                 addiu   $a0, $s0, 0x6C ; ERIC: context for RC4 algorithm 1
	ROM:804A7064                 move    $a1, $v0 ; ERIC: MD5 return from Network__GetSessionKey1
	ROM:804A7068                 jal     RC4_Init
	ROM:804A706C                 li      $a2, 0x10 ; ERIC: size of key (MD5 digest length)
	ROM:804A7070                 lw      $a0, 0x80001274
	ROM:804A7074                 jal     Network__GetSessionKey2
	ROM:804A7078                 lw      $a1, 0x24($s0)
	ROM:804A707C                 addiu   $a0, $s0, 0x178 ; ERIC: context for RC4 algorithm 2
	ROM:804A7080                 move    $a1, $v0 ; ERIC: MD5 return from Network__GetSessionKey2
	ROM:804A7084                 jal     RC4_Init
	ROM:804A7088                 li      $a2, 0x10 ; ERIC: size of key (MD5 digest length)
	ROM:804A708C                 li      $v0, 1
	ROM:804A7090                 sb      $v0, 0x284($s0)
	ROM:804A7094                 lw      $ra, 0x20+var_8($sp)
	ROM:804A7098                 lw      $s1, 0x20+var_C($sp)
	ROM:804A709C                 lw      $s0, 0x20+var_10($sp)
	ROM:804A70A0                 move    $v0, $zero
	ROM:804A70A4                 jr      $ra
	ROM:804A70A8                 addiu   $sp, 0x20
	ROM:804A70A8  # End of function WTVProtocol__SetSessionKeys
	ROM:80497ADC Network__GetSessionKey1:                 # CODE XREF: WTVProtocol__SetSessionKeys+1C↓p
	ROM:80497ADC
	ROM:80497ADC var_40          = -0x40
	ROM:80497ADC var_30          = -0x30
	ROM:80497ADC var_2C          = -0x2C
	ROM:80497ADC var_18          = -0x18
	ROM:80497ADC var_10          = -0x10
	ROM:80497ADC var_C           = -0xC
	ROM:80497ADC var_8           = -8
	ROM:80497ADC
	ROM:80497ADC                 addiu   $sp, -0x50
	ROM:80497AE0                 sw      $s1, 0x50+var_C($sp)
	ROM:80497AE4                 sw      $s0, 0x50+var_10($sp)
	ROM:80497AE8                 move    $s0, $a1
	ROM:80497AEC                 addiu   $s1, $a0, 0x98 ; ERIC: FROM 8049A46C:Network__ProcessChallenge
	ROM:80497AF0                 move    $a1, $s1
	ROM:80497AF4                 sw      $ra, 0x50+var_8($sp)
	ROM:80497AF8                 addiu   $a0, $sp, 0x50+var_40
	ROM:80497AFC                 jal     wtv_memcpy
	ROM:80497B00                 li      $a2, 0x10
	ROM:80497B04                 sw      $s0, 0x50+var_18($sp)
	ROM:80497B08                 addiu   $a0, $sp, 0x50+var_30
	ROM:80497B0C                 addiu   $a1, $sp, 0x50+var_18 ; ERIC: wtv-incarnation number.  Incremented each time a new RC4 session starts
	ROM:80497B10                 jal     wtv_memcpy
	ROM:80497B14                 li      $a2, 4
	ROM:80497B18                 move    $a1, $s1 ; ERIC: session key repeated
	ROM:80497B1C                 addiu   $a0, $sp, 0x50+var_2C
	ROM:80497B20                 jal     wtv_memcpy
	ROM:80497B24                 li      $a2, 0x10
	ROM:80497B28                 li      $a2, 0x8000D1C8
	ROM:80497B30                 addiu   $a0, $sp, 0x50+var_40
	ROM:80497B34                 jal     MD5
	ROM:80497B38                 li      $a1, 0x24
	ROM:80497B3C                 lw      $ra, 0x50+var_8($sp)
	ROM:80497B40                 lw      $s1, 0x50+var_C($sp)
	ROM:80497B44                 lw      $s0, 0x50+var_10($sp)
	ROM:80497B48                 jr      $ra
	ROM:80497B4C                 addiu   $sp, 0x50
	ROM:80497B4C  # End of function Network__GetSessionKey1
	ROM:80497B50 Network__GetSessionKey2:                 # CODE XREF: WTVProtocol__SetSessionKeys+38↓p
	ROM:80497B50
	ROM:80497B50 var_40          = -0x40
	ROM:80497B50 var_30          = -0x30
	ROM:80497B50 var_2C          = -0x2C
	ROM:80497B50 var_18          = -0x18
	ROM:80497B50 var_10          = -0x10
	ROM:80497B50 var_C           = -0xC
	ROM:80497B50 var_8           = -8
	ROM:80497B50
	ROM:80497B50                 addiu   $sp, -0x50
	ROM:80497B54                 sw      $s1, 0x50+var_C($sp)
	ROM:80497B58                 sw      $s0, 0x50+var_10($sp)
	ROM:80497B5C                 move    $s0, $a1
	ROM:80497B60                 addiu   $s1, $a0, 0xA8 ; ERIC: FROM 8049A47C:Network__ProcessChallenge
	ROM:80497B64                 move    $a1, $s1
	ROM:80497B68                 sw      $ra, 0x50+var_8($sp)
	ROM:80497B6C                 addiu   $a0, $sp, 0x50+var_40
	ROM:80497B70                 jal     wtv_memcpy
	ROM:80497B74                 li      $a2, 0x10
	ROM:80497B78                 sw      $s0, 0x50+var_18($sp)
	ROM:80497B7C                 addiu   $a0, $sp, 0x50+var_30
	ROM:80497B80                 addiu   $a1, $sp, 0x50+var_18 ; ERIC: wtv-incarnation number.  Incremented each time a new RC4 session starts
	ROM:80497B84                 jal     wtv_memcpy
	ROM:80497B88                 li      $a2, 4
	ROM:80497B8C                 move    $a1, $s1 ; ERIC: session key repeated
	ROM:80497B90                 addiu   $a0, $sp, 0x50+var_2C
	ROM:80497B94                 jal     wtv_memcpy
	ROM:80497B98                 li      $a2, 0x10
	ROM:80497B9C                 li      $a2, 0x8000D1C8
	ROM:80497BA4                 addiu   $a0, $sp, 0x50+var_40
	ROM:80497BA8                 jal     MD5
	ROM:80497BAC                 li      $a1, 0x24
	ROM:80497BB0                 lw      $ra, 0x50+var_8($sp)
	ROM:80497BB4                 lw      $s1, 0x50+var_C($sp)
	ROM:80497BB8                 lw      $s0, 0x50+var_10($sp)
	ROM:80497BBC                 jr      $ra
	ROM:80497BC0                 addiu   $sp, 0x50
	ROM:80497BC0  # End of function Network__GetSessionKey2
	"""

	def SecureOn(self):
		hMD5 = MD5.new()
		hMD5.update(self.session_key1 + self.incarnation.to_bytes(4, byteorder='big') + self.session_key1)
		self.hRC4_Key1 = ARC4.new(hMD5.digest())

		hMD51 = MD5.new()
		hMD51.update(self.session_key2 + self.incarnation.to_bytes(4, byteorder='big') + self.session_key2)
		self.hRC4_Key2 = ARC4.new(hMD5.digest())

	def EncryptKey1(self, data):
		return self.Encrypt(self.hRC4_Key1, data)

	def EncryptKey2(self, data):
		return self.Encrypt(self.hRC4_Key2, data)

	def Encrypt(self, context, data):
		if context != None:
			return context.encrypt(data)
		else:
			raise Exception("Invalid RC4 encryption context")

	def DecryptKey1(self, data):
		return self.Decrypt(self.hRC4_Key1, data)

	def DecryptKey2(self, data):
		return self.Decrypt(self.hRC4_Key2, data)

	def Decrypt(self, context, data):
		if context != None:
			return context.decrypt(data)
		else:
			raise Exception("Invalid RC4 decryption context")


	"""
	ERIC: The RC4 stream doesn't start until "SECURE ON" is sent to the server.

	ROM:804A6DE0 WTVProtocol__IdleSecureBegin:            # DATA XREF: ROM:806D3DF4↓o
	ROM:804A6DE0
	ROM:804A6DE0 var_18          = -0x18
	ROM:804A6DE0 var_14          = -0x14
	ROM:804A6DE0 var_10          = -0x10
	ROM:804A6DE0 var_C           = -0xC
	ROM:804A6DE0 var_8           = -8
	ROM:804A6DE0
	ROM:804A6DE0                 addiu   $sp, -0x28
	ROM:804A6DE4                 sw      $s2, 0x28+var_10($sp)
	ROM:804A6DE8                 lui     $a1, 0x8000
	ROM:804A6DEC                 sw      $ra, 0x28+var_8($sp)
	ROM:804A6DF0                 sw      $s3, 0x28+var_C($sp)
	ROM:804A6DF4                 sw      $s1, 0x28+var_14($sp)
	ROM:804A6DF8                 sw      $s0, 0x28+var_18($sp)
	ROM:804A6DFC                 lw      $v1, 0x80001410
	ROM:804A6E00                 move    $s2, $a0
	ROM:804A6E04                 lw      $v0, 0x10($s2)
	ROM:804A6E08                 sw      $v1, 0x24($s2)
	ROM:804A6E0C                 lw      $v0, 4($v0)
	ROM:804A6E10                 addiu   $v1, 1
	ROM:804A6E14                 xori    $v0, 1
	ROM:804A6E18                 andi    $v0, 1
	ROM:804A6E1C                 beqz    $v0, loc_804A6EFC
	ROM:804A6E20                 sw      $v1, 0x80001410
	ROM:804A6E24                 lui     $s3, 0x8000
	ROM:804A6E28                 lw      $v1, 0x80001274
	ROM:804A6E2C                 lbu     $v0, 0x139($v1)
	ROM:804A6E30                 beqz    $v0, loc_804A6E40
	ROM:804A6E34                 move    $a0, $zero
	ROM:804A6E38                 lbu     $v0, 0x122($v1)
	ROM:804A6E3C                 sltu    $a0, $zero, $v0
	ROM:804A6E40
	ROM:804A6E40 loc_804A6E40:                            # CODE XREF: WTVProtocol__IdleSecureBegin+50↑j
	ROM:804A6E40                 beqz    $a0, loc_804A6EFC
	ROM:804A6E44                 addiu   $s0, $s2, 0x28
	ROM:804A6E48                 la      $a1, aSecureOn   # "SECURE ON"
	ROM:804A6E50                 jal     Stream__WriteString
	ROM:804A6E54                 move    $a0, $s0
	ROM:804A6E58                 la      $s1, dword_806D3AD8
	ROM:804A6E60                 move    $a0, $s0
	ROM:804A6E64                 jal     Stream__WriteString
	ROM:804A6E68                 move    $a1, $s1
	ROM:804A6E6C                 lui     $a2, 0x8000
	ROM:804A6E70                 lui     $a1, 0x806D
	ROM:804A6E74                 li      $a2, 0x800024A0
	ROM:804A6E78                 la      $a1, aAcceptLanguage_0  # "Accept-Language"
	ROM:804A6E7C                 jal     Stream__WriteAttribute
	ROM:804A6E80                 move    $a0, $s0
	ROM:804A6E84                 lw      $a0, 0x1274($s3)
	ROM:804A6E88                 lw      $v0, 4($a0)
	ROM:804A6E8C                 lw      $v0, 0xC($v0)
	ROM:804A6E90                 jalr    $v0
	ROM:804A6E94                 move    $a1, $s0
	ROM:804A6E98                 jal     System__WriteHeaders
	ROM:804A6E9C                 move    $a0, $s0
	ROM:804A6EA0                 la      $a1, aWtvIncarnation_0  # "wtv-incarnation:"
	ROM:804A6EA8                 sb      $zero, 0x1C($s2)
	ROM:804A6EAC                 jal     Stream__WriteString
	ROM:804A6EB0                 move    $a0, $s0
	ROM:804A6EB4                 lw      $a1, 0x24($s2)
	ROM:804A6EB8                 jal     Stream__WriteNumeric
	ROM:804A6EBC                 move    $a0, $s0
	ROM:804A6EC0                 move    $a0, $s0
	ROM:804A6EC4                 jal     Stream__WriteString
	ROM:804A6EC8                 move    $a1, $s1
	ROM:804A6ECC                 move    $a0, $s0
	ROM:804A6ED0                 jal     Stream__WriteString
	ROM:804A6ED4                 move    $a1, $s1
	ROM:804A6ED8                 move    $a0, $s2
	ROM:804A6EDC                 jal     Protocol__SetState
	ROM:804A6EE0                 li      $a1, 4
	ROM:804A6EE4                 lw      $v0, 0x20($s2)
	ROM:804A6EE8                 lw      $v0, 0x28($v0)
	ROM:804A6EEC                 jalr    $v0
	ROM:804A6EF0                 move    $a0, $s2
	ROM:804A6EF4                 j       loc_804A6F0C
	ROM:804A6EF8                 lw      $ra, 0x28+var_8($sp)
	ROM:804A6EFC  # ---------------------------------------------------------------------------
	ROM:804A6EFC
	ROM:804A6EFC loc_804A6EFC:                            # CODE XREF: WTVProtocol__IdleSecureBegin+3C↑j
	ROM:804A6EFC                                          # WTVProtocol__IdleSecureBegin:loc_804A6E40↑j
	ROM:804A6EFC                 move    $a0, $s2
	ROM:804A6F00                 jal     Protocol__SetState
	ROM:804A6F04                 li      $a1, 5
	ROM:804A6F08                 lw      $ra, 0x28+var_8($sp)
	ROM:804A6F0C
	ROM:804A6F0C loc_804A6F0C:                            # CODE XREF: WTVProtocol__IdleSecureBegin+114↑j
	ROM:804A6F0C                 lw      $s3, 0x28+var_C($sp)
	ROM:804A6F10                 lw      $s2, 0x28+var_10($sp)
	ROM:804A6F14                 lw      $s1, 0x28+var_14($sp)
	ROM:804A6F18                 lw      $s0, 0x28+var_18($sp)
	ROM:804A6F1C                 jr      $ra
	ROM:804A6F20                 addiu   $sp, 0x28
	ROM:804A6F20  # End of function WTVProtocol__IdleSecureBegin
	"""

def handle_challenge(chl: str, key: str):
    s = WTVNetworkSecurity(key)
    a = s.ProcessChallenge(chl)
    print(a)

#handle_challenge("SMJXj9fsvyycF0afhCeOzUBRhBbG0/ni0bKJmXNrL0JLf/eHoj5LYvO6VvmzROYfrTHmXMT+rfsNJULkI93ArZ+dret8JmAiUaCd0FmQyvTXTzBrEvUgYr3DhkOT6xzY9LiOwV1RW14W7Kh0", "FFocoqh87fs=")