# 전역
total_size = 64                         # 전체 메모리 크기 64바이트 (2의 거듭제곱)
max_order = total_size.bit_length() - 1 # ex) 6 = 64.bit_length() -1

# free_lists[k] = 크기 2^k 블록들의 시작 주소 리스트
free_lists = {i: [] for i in range(max_order + 1)}
free_lists[max_order] = [0]             # 초기에는 전체 메모리 하나만 남아 있음
# free_lists = {
#    0: [],   # 2^0 바이트 블록의 빈 주소 리스트
#    1: [],   # 2^1 바이트 블록의 빈 주소 리스트
#    2: [],   # …
#    …,
#    max_order: []  # 2^max_order 바이트 블록의 빈 주소 리스트
# }


# allocations[addr] = order  (addr에서 시작하는 블록의 order)
allocations = {}


def order_for_size(size):
    """요청한 size를 담을 수 있는 최소 2의 거듭제곱(order) 계산"""
    order = 0
    block = 1
    while block < size:
        block <<= 1
        order += 1
    return order

def allocate(size):
    """size 바이트 요청 → 2^order 블록 할당, 시작 주소 반환"""
    order = order_for_size(size)
    # order 이상의 블록 중 첫 번째 사용 가능한 것 찾기
    for o in range(order, max_order + 1):
        if free_lists[o]:
            chosen = o
            break
    else:
        raise MemoryError("메모리 부족")

    addr = free_lists[chosen].pop(0)

    # 너무 큰 블록은 반으로 쪼개서(buddy를 free_lists에 넣고) 내려가기
    while chosen > order:
        chosen -= 1
        buddy = addr + (1 << chosen)
        free_lists[chosen].append(buddy)

    allocations[addr] = order
    return addr

def free(addr):
    """addr에서 시작하는 블록 해제 → 가능하면 버디와 병합"""
    if addr not in allocations:
        raise ValueError("잘못된 주소 해제")
    order = allocations.pop(addr)
    cur = addr

    # 같은 order 리스트에 버디가 있으면 꺼내서 합치기 반복
    while order < max_order:
        buddy = cur ^ (1 << order)
        if buddy in free_lists[order]:
            free_lists[order].remove(buddy)
            cur = min(cur, buddy)
            order += 1
        else:
            break

    free_lists[order].append(cur)

def dump():
    """현재 할당/빈 블록 상태 출력"""
    print("=== Allocations ===")
    if not allocations:
        print(" (없음)")
    else:
        for addr, order in sorted(allocations.items()):
            print(f" Addr {addr}, Size {1<<order}")
    print("\n=== Free Lists ===")
    for k in range(max_order + 1):
        print(f" Order {k} (Size {1<<k}): {free_lists[k]}")

# ── 실행 예시 ──
if __name__ == "__main__":
    print("== 초기 상태 ==")
    dump()

    a1 = allocate(10)   # 실제로는 16바이트 블록 할당
    a2 = allocate(20)   # 32바이트 블록
    a3 = allocate(5)    # 8바이트 블록
    print("\n== 할당 후 상태 ==")
    dump()

    free(a2)
    print(f"\n==주소 {a2} 해제 후 상태 ==")
    dump()

    a4 = allocate(18)   # 32바이트 블록
    print(f"\n== 18바이트 할당 → Addr {a4} ==")
    dump()
