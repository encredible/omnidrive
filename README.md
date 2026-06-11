# OmniDrive (드라이브/스토리지 컴포넌트)

Bilingual: [한국어](#한국어) | [English](#english)

---

## 한국어

OmniDrive는 **j1010red / JKUniverse** 생태계의 통합 가상 디스크 스토리지, 웹 대시보드 및 심볼릭 링크 관리 도구입니다. macOS의 `.sparsebundle.sparseimage` 디스크 이미지를 기반으로 로컬 스토리지, Google Drive, iCloud Drive, 프로젝트 작업 영역(Workspaces) 등을 하나의 마운트 포인트(`/Volumes/OmniDrive`)로 통합하여 기기 간(MacBook Pro ↔ Mac Mini) 완벽한 동기화 및 파일 관리를 가능하게 합니다.

### 핵심 기능

* **가상 디스크 통합 마운트**: 복잡한 클라우드 및 로컬 경로를 `/Volumes/OmniDrive` 아래에 하나로 통일.
* **웹 관리 대시보드 (Docker 지원)**: 마운트 상태, 파일 브라우저, 디스크 용량 모니터링, 심볼릭 링크 상태를 웹 브라우저에서 한눈에 제어 가능.
* **심볼릭 링크 관리**: 마운트 즉시 Google Drive, iCloud, 개발 프로젝트의 심볼릭 링크 자동 생성 및 유효성 검사.
* **Tailscale/LAN SMB 공유**: 타 기기에서 SMB 프로토콜(`mount_smbfs`)로 가상 디스크에 원격 접근 및 협업 지원.
* **macOS 런처 앱 컴파일**: Spotlight 또는 Dock에서 바로 실행할 수 있는 AppleScript 런처 앱 제공.
* **프리미엄 CLI 인터페이스**: `j` 커맨드 센터 스타일의 터미널 UI 지원.

### 설치 및 웹 실행 방법

#### 1. 로컬 환경에서 설치 및 실행
패키지를 설치합니다:

```bash
cd /Users/jack/.gemini/antigravity/scratch/omnidrive
pip install -e .
```

웹 대시보드를 실행합니다:
```bash
python3 -m uvicorn omnidrive.web:app --host 0.0.0.0 --port 8000 --reload
```
브라우저에서 `http://localhost:8000`으로 접속할 수 있습니다.

#### 2. Docker를 이용한 배포
도커 컨테이너를 빌드하고 백그라운드에서 실행합니다:
```bash
docker compose up --build -d
```
도커 컨테이너가 호스트의 마운트 볼륨(`/Volumes/OmniDrive`) 및 디스크 이미지 디렉토리를 바인딩하여 자동으로 상태를 동기화합니다.

### CLI 사용법

#### 1. 마운트 상태 확인
```bash
omni status
```

#### 2. 가상 디스크 마운트
```bash
omni mount
```

#### 3. 심볼릭 링크 복구/재생성
```bash
omni link
```

---

## English

OmniDrive is a unified virtual disk storage, web dashboard, and symlink manager for the **j1010red / JKUniverse** ecosystem. Built on top of macOS `.sparsebundle.sparseimage` disk images, it consolidates local storages, Google Drive, iCloud Drive, and development workspaces into a single mount point (`/Volumes/OmniDrive`), enabling seamless cross-device synchronization and management (MacBook Pro ↔ Mac Mini).

### Key Features

* **Unified Virtual Disk**: Consolidates separate cloud and local folders under `/Volumes/OmniDrive`.
* **Web Control Dashboard (Docker Ready)**: Inspect mount status, files, storage capacity, and symlink health from any web browser.
* **Symlink Management**: Automatically builds and validates symlinks to Google Drive, iCloud, and workspaces on mount.
* **Cross-Device Sharing**: Supports mounting the virtual disk from remote clients over Tailscale/LAN via SMB (`mount_smbfs`).
* **Launcher Applet Compilation**: Compiles a native macOS AppleScript application for easy launching.
* **Terminal CLI**: Features a colored console UI matching the central `j` Command Center design.

### Installation & Running Web App

#### 1. Local Native Setup
Install the package in editable mode:

```bash
cd /Users/jack/.gemini/antigravity/scratch/omnidrive
pip install -e .
```

Start the FastAPI web dashboard:
```bash
python3 -m uvicorn omnidrive.web:app --host 0.0.0.0 --port 8000 --reload
```
Open `http://localhost:8000` in your browser.

#### 2. Docker Deployment
Build and run the container in detached mode:
```bash
docker compose up --build -d
```
The Docker container binds the host's virtual mount point and disk image folder for seamless synchronization.

### CLI Usage

```bash
omni status     # Check mount and symlink health
omni mount      # Attach the virtual sparseimage
omni unmount    # Detach the mount point safely
omni link       # Repair and recreate missing symlinks
```
