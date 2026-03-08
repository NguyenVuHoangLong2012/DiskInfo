import sys
import ctypes
def get_logical_drives():
	Mask = ctypes.windll.kernel32.GetLogicalDrives()
	Drives = []
	for I in range(26):
		if Mask & (1 << I):
			Drives.append(f"{chr(65 + I)}:\\")
	return Drives
def getDriveUsage(Drive):
	Free = ctypes.c_ulonglong()
	Total = ctypes.c_ulonglong()
	Total_Free = ctypes.c_ulonglong()
	Result = ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(Drive), ctypes.byref(Free), ctypes.byref(Total), ctypes.byref(Total_Free))
	if not Result:
		return None
	Used = Total.value - Free.value
	Percent = (Used / Total.value) * 100 if Total.value else 0
	return {
		"total": Total.value,
		"used": Used,
		"free": Free.value,
		"percent": Percent
	}
def getVolumeInfo(Drive):
	if not Drive.endswith("\\"):
		Drive += "\\"
	Volume_name_buffer = ctypes.create_unicode_buffer(261)
	Fs_name_buffer = ctypes.create_unicode_buffer(261)
	Result = ctypes.windll.kernel32.GetVolumeInformationW(ctypes.c_wchar_p(Drive), Volume_name_buffer, len(Volume_name_buffer), None, None, None, Fs_name_buffer, len(Fs_name_buffer))
	if Result:
		return [
			Volume_name_buffer.value,
			Fs_name_buffer.value
		]
	else:
		return None
def getDriveType(Drive):
	return ctypes.windll.kernel32.GetDriveTypeW(ctypes.c_wchar_p(Drive))
def formatSize(N):
	return f"{N / (1024 ** 3):.2f}"
def showFull():
	Partitions = get_logical_drives()
	for Partition in Partitions:
		Info = getVolumeInfo(Partition)
		Drive_Type = getDriveType(Partition)
		print("Volume:", Partition.replace("\\", ""))
		if Info:
			print("Label:", Info[0] or "No label")
		else:
			print("Label: <unavailable>")
		if Drive_Type == 2:
			print("Type: USB drive")
		elif Drive_Type == 5:
			print("Type: CD/DVD drive")
		elif Drive_Type == 4:
			print("Type: Network drive")
		elif Drive_Type == 3:
			print("Type: Local disk drive")
		elif Drive_Type == 6:
			print("Type: Ram disk drive")
		else:
			print("Type: Unknown")
		if Info:
			print("File system:", Info[1] or "Unknown")
		else:
			print("File system: <unavailable>")
		try:
			Usage = getDriveUsage(Partition)
			if Usage:
				Used = Usage["used"]
				Percent = Usage["percent"]
				Free = Usage["free"]
				Total = Usage["total"]
				print(f"Used space: {formatSize(Used)} GB ({Used} Bytes)")
				print(f"Used percentage: {Percent:.2f}%")
				print(f"Free space: {formatSize(Free)} GB ({Free} Bytes)")
				print(f"Capacity: {formatSize(Total)} GB ({Total} Bytes)")
			else:
				print("Disk usage: unavailable")
		except Exception as Error:
			print("Error, cannot get drive information: ", Error)
	sys.exit(0)
def showAllDrive(Label=False):
	Partitions = get_logical_drives()
	Seen = set()
	for Partition in Partitions:
		Volume = Partition
		Volume_Name = Volume.replace("\\", "")
		if Volume not in Seen:
			Seen.add(Volume)
			if Label:
				Info = getVolumeInfo(Volume)
				Label_Name = Info[0] if Info and Info[0] else "No label"
				print(f"{Label_Name} ({Volume_Name})")
			else:
				print(Volume_Name)
	sys.exit(0)
def main():
	if len(sys.argv) < 2:
		showFull()
	else:
		Flag = sys.argv[1]
		if Flag.lower().startswith(("/n", "-n")):
			showAllDrive(Label=True)
		elif Flag.lower().startswith(("/l", "-l")):
			showAllDrive(Label=False)
		else:
			print("Unknown option: ", Flag)
			sys.exit(1)
if __name__ == "__main__":
	main()