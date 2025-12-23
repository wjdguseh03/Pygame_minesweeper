# Minesweeper (지뢰찾기 게임)

Pygame을 이용해 구현한 지뢰찾기 게임입니다.  
기존에서 총 5가지 기능을 추가 구현했습니다.

---

## 구현된 기능

### 1. 난이도 설정 기능

게임 시작 전 난이도를 선택할 수 있으며,  
난이도에 따라 게임 판 크기와 지뢰 개수가 달라집니다.
**숫자 키 `1`을 누르면 Easy, `2`는 Normal, `3`은 Hard가 선택됩니다.**

- **Easy**: 10 × 10, 10 mines  
- **Normal**: 16 × 16, 40 mines  
- **Hard**: 25 × 25, 99 mines  

난이도 선택 시 보드는 해당 설정으로 초기화되며,  
게임이 시작된 이후에는 난이도를 변경할 수 없습니다.

**Easy**

![Image](https://github.com/user-attachments/assets/a5a1052d-f870-40a2-a5aa-87e7712c17e9)

**Normal**

![Image](https://github.com/user-attachments/assets/1ae36cfd-2cc2-4dd8-ae6b-74f9bdb5d926)

**Hard**

![Image](https://github.com/user-attachments/assets/07c15262-1637-4c11-b217-b8bd5cf8b804)


---

### 2. 힌트 기능

게임 진행 중 힌트를 사용할 수 있으며,  
지뢰가 아닌 칸 중 아직 확인되지 않은 칸을 **임의로 한 칸 공개**합니다.

- 이미 열려 있는 칸 또는 지뢰 칸은 힌트 대상에서 제외됩니다.
- 힌트 사용 횟수는 제한되어 있으며 기본값은 **3회**
- `H` 키를 눌러 힌트 사용 가능
- 화면 상단에 힌트 사용 횟수 조회 가능

**힌트를 쓰지 않은 상태(Hints:3)**

![Image](https://github.com/user-attachments/assets/41c04d2d-9399-4c4b-a53a-63c3b8288b7c)


**힌트를 모두 사용한 상태(Hints:0)**

![Image](https://github.com/user-attachments/assets/b50a3023-3d0d-4273-acbd-d66f7688622d)


---

### 3. 게임 종료 시 입력 차단 기능

게임이 종료된 상태에서는  
추가적인 마우스 입력이 동작하지 않도록 구현했습니다.

- 셀 클릭, 깃발 표시 등 모든 입력 차단
- 재시작 버튼 클릭 또는 `R` 키 입력 시에만 다시 입력 가능

**이 기능은 스크린샷으로 확인하기 힘드므로 첨부하지 않겠습니다.**

---

### 4. 게임 종료 시 결과 메시지 + 재시작 버튼

게임 종료 시 화면에 결과 메시지를 표시합니다.

- 패배 시: **GAME OVER**
- 승리 시: **GAME CLEAR**

결과 메시지 아래에는 **RESTART 버튼**이 표시되며,  
마우스 클릭 또는 `R` 키 입력으로 새 게임을 시작할 수 있습니다.  
재시작 시 보드는 완전히 초기화됩니다.

**게임 패배 시 Game Over 및 RESTART 버튼**

![Image](https://github.com/user-attachments/assets/675705fd-750b-499b-ac1c-8fdba1531047)


**게임 승리 시 Game Clear 및 RESTART 버튼**

![Image](https://github.com/user-attachments/assets/00bdb7f5-cbb6-4ed3-a562-d69e5d47481c)

---

### 5. 하이 스코어 저장 및 표출 기능

게임 클리어 시 플레이 시간을 기준으로 하이 스코어를 기록합니다.

- 클리어 시간(mm:ss 형식)을 highscore.txt 파일에 저장
- 기존 기록보다 빠를 경우 갱신, 느릴 경우 기존 최고 기록 출력
- 게임 종료 화면에서 재시작 버튼 밑에 하이 스코어를 함께 표시

**기존 기록에서 하이 스코어 갱신**

![Image](https://github.com/user-attachments/assets/6c5efe6b-5f98-4344-86b4-e9fcf1a1f227)
