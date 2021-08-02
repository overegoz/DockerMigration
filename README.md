# DockerMigration

To implement different docker migration methods.

Code is partially from
- https://github.com/GEONheong/migrate_docker_conatiner_diff.git
- https://github.com/GEONheong/migrate_docker_container_fullCopy.git
- https://github.com/KimJaeHwan/docker_live_migration.git
- School of SW, Hallym Univ., South Korea

# Important
- Ubuntu 18.04, Docker 17 버전(저장된 폴더: `./DockerCheckpoint`) 조합으로 checkpoint 기능을 사용함
	- Docker 17 버전 저장된 폴더: `./DockerCheckpoint`
	- Ubuntu 20.04, Docker 최신버전 사용 시, checkpoint 기능이 동작안함 (2021.07 기준)
- Checkpoint 기능을 사용하기 위해서는 CRIU 설치가 필요함
	- 설치방법은 `./DockerCheckpoint` 폴더 확인
	- [공식 github](https://github.com/checkpoint-restore/criu)에서 다운받아서 설치했음
	- 내가 사용한 CRIU 버전은 3.15 (저장된 폴더 : `./DockerCheckpoint`)
	- CRIU 버전 확인 명령어는 ~~모르겠고~~, CRIU 공식 github에서 다운 받은 파일 중 `/Makefile.versions` 파일에 기록된 버전 정보로 확인함
- Ubuntu 18.04 커널 버전 : 5.4.0-80-generic ($ uname -r 명령으로 확인)

# 실행 방법
1. `Profile.py'
	- 기존에 생성된 프로파일 정보를 확인, 또는
	- 새로 생성한 프로파일에 대한 정보를 기록하기 (dictionary 자료구조, <프로파일 번호>:<값> 형태로 입력)
2. `common.py`
	- 사전에 정의된 행동(predefined action)을 `action_profile` 함수 안에 코딩
3. ㅁㅁ
	1. ㅁㅁ
	2. ㅁㅁ
4. ㅁㅁ