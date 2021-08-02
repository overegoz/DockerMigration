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
	- 새로 생성한 프로파일에 대한 정보를 기록하기 (dictionary 자료구조, <프로파일 번호>:<값> 형태로 프로파일별로 값/정보를 입력)
2. `common.py` : 사전에 정의된 행동(predefined action)을 `action_profile` 함수 안에 코딩
	- AP-1에서 동작하는 ES-1는 '행동'을 스레드로 1회 실행함
	- AP-2에서 동작하는 ES-2는, log-replay로 migr 된 경우, '행동'을 스레드 없이 1회 실행함. 실행 완료한 후에 연결된 AP-2 에게 READY 메시지를 보내서 서비스 가능 상태가 되었다는 것을 알림
3. 새로운 프로파일(예: Profile-X)을 만들었을 경우, 해당 프로파일에 대한 도커 이미지 생성을 준비해야 함
	1. `\src\docker-images`에서 Profile-X 폴더를 만들고, 그 안에 ES-1, ES-2 폴더를 만들기
	2. ES-1, ES-2 폴더 내의 `build.sh`파일과 `Dockerfile` 파일에서 프로파일 번호 관련 부분을 수정하기 (나머지 *.py 파일은 자동으로 생성되는 파일이니까, 무시하기)
	3. `./build-img-edgeServer1.sh`, `./build-img-edgeServer1.sh` 파일에서 
4. ㅁㅁ