# DockerMigration

To implement different docker migration methods.

Code is partially from
- https://github.com/GEONheong/migrate_docker_conatiner_diff.git
- https://github.com/GEONheong/migrate_docker_container_fullCopy.git
- https://github.com/KimJaeHwan/docker_live_migration.git
- School of SW, Hallym Univ., South Korea

# Important
- Ubuntu 20.04, Docker 최신버전은 checkpoint 기능이 동작안함
- Ubuntu 18.04, Docker 17 버전(저장된 폴더: `./DockerCheckpoint`)은 checkpoint 기능이 동작함
	- Docker 17 버전 저장된 폴더: `./DockerCheckpoint`
- Checkpoint 기능을 사용하기 위해서는 CRIU 설치가 필요함
	- 설치방법은 `./DockerCheckpoint` 폴더 확인
	- [공식 github](https://github.com/checkpoint-restore/criu)에서 다운받아서 설치했음
	- 내가 사용한 CRIU 버전은 3.15 (저장된 폴더 : `./DockerCheckpoint`)
	- CRIU 버전 확인 명령어는 ~~모르겠고~~, github에서 다운 받은 파일 중 `/Makefile.versions` 파일에 기록된 버전 정보로 확인함
- Ubuntu 18.04 커널 버전 : 5.4.0-80-generic ($ uname -r 명령으로 확인)

# 실행 방법
1. `common.py`
	- ㅁㅁ
2. ㅁㅁ
	1. ㅁㅁ
	2. ㅁㅁ
3. ㅁㅁ