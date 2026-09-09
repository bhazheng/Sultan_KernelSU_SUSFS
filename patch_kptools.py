#!/usr/bin/env python3
import sys, os

def patch_kallsym_c(kallsym_path):
    if os.path.isdir(kallsym_path):
        kallsym_path = os.path.join(kallsym_path, "tools", "kallsym.c")
    if not os.path.exists(kallsym_path):
        print(f"[!] File not found: {kallsym_path}")
        return False

    with open(kallsym_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "load_system_map" in content:
        print("[*] kallsym.c already contains load_system_map (patch already applied).")
        return True

    helper_code = r'''
#include <unistd.h>

static int load_system_map(kallsym_t *info, char *img, int32_t imglen)
{
    const char *map_path = getenv("SYSTEM_MAP");
    if (!map_path || !map_path[0]) {
        if (access("out/System.map", R_OK) == 0) map_path = "out/System.map";
        else if (access("System.map", R_OK) == 0) map_path = "System.map";
    }
    if (!map_path || access(map_path, R_OK) != 0) {
        return -1;
    }
    FILE *fp = fopen(map_path, "r");
    if (!fp) return -1;

    tools_logi("Loading symbol references from System.map (%s)...\n", map_path);
    char line[512];
    uint64_t va_banner = 0;
    uint64_t va_token_table = 0;
    uint64_t va_token_index = 0;
    uint64_t va_markers = 0;
    uint64_t va_names = 0;
    uint64_t va_num_syms = 0;
    uint64_t va_offsets = 0;
    uint64_t va_addresses = 0;
    uint64_t va_relative_base = 0;

    while (fgets(line, sizeof(line), fp)) {
        uint64_t addr = 0;
        char type = 0;
        char name[256] = {0};
        if (sscanf(line, "%lx %c %255s", &addr, &type, name) == 3) {
            if (!strcmp(name, "linux_banner")) va_banner = addr;
            else if (!strcmp(name, "kallsyms_token_table")) va_token_table = addr;
            else if (!strcmp(name, "kallsyms_token_index")) va_token_index = addr;
            else if (!strcmp(name, "kallsyms_markers")) va_markers = addr;
            else if (!strcmp(name, "kallsyms_names")) va_names = addr;
            else if (!strcmp(name, "kallsyms_num_syms")) va_num_syms = addr;
            else if (!strcmp(name, "kallsyms_offsets")) va_offsets = addr;
            else if (!strcmp(name, "kallsyms_addresses")) va_addresses = addr;
            else if (!strcmp(name, "kallsyms_relative_base")) va_relative_base = addr;
        }
    }
    fclose(fp);

    if (!va_banner || !va_token_table) {
        tools_logw("System.map parsed but missing linux_banner or kallsyms_token_table\n");
        return -1;
    }

    if (info->banner_num <= 0) {
        find_linux_banner(info, img, imglen, NULL);
    }
    if (info->banner_num <= 0) {
        tools_logw("Cannot locate linux_banner in image\n");
        return -1;
    }

    uint64_t va_offset = va_banner - (uint64_t)info->linux_banner_offset[0];
    tools_logi("Calculated kernel VA offset: 0x%016lx (banner VA: 0x%016lx, file offset: 0x%08x)\n",
               (unsigned long)va_offset, (unsigned long)va_banner, info->linux_banner_offset[0]);

    if (va_token_table > va_offset) {
        info->kallsyms_token_table_offset = (int32_t)(va_token_table - va_offset);
        tools_logi("System.map -> kallsyms_token_table offset: 0x%08x\n", info->kallsyms_token_table_offset);
    }
    if (va_token_index > va_offset) {
        info->kallsyms_token_index_offset = (int32_t)(va_token_index - va_offset);
        tools_logi("System.map -> kallsyms_token_index offset: 0x%08x\n", info->kallsyms_token_index_offset);
    }
    if (va_markers > va_offset) {
        info->kallsyms_markers_offset = (int32_t)(va_markers - va_offset);
        tools_logi("System.map -> kallsyms_markers offset: 0x%08x\n", info->kallsyms_markers_offset);
    }
    if (va_names > va_offset) {
        info->kallsyms_names_offset = (int32_t)(va_names - va_offset);
        tools_logi("System.map -> kallsyms_names offset: 0x%08x\n", info->kallsyms_names_offset);
    }
    if (va_num_syms > va_offset) {
        info->kallsyms_num_syms_offset = (int32_t)(va_num_syms - va_offset);
        tools_logi("System.map -> kallsyms_num_syms offset: 0x%08x\n", info->kallsyms_num_syms_offset);
    }
    if (va_offsets > va_offset) {
        info->kallsyms_offsets_offset = (int32_t)(va_offsets - va_offset);
        info->has_relative_base = 1;
        tools_logi("System.map -> kallsyms_offsets offset: 0x%08x\n", info->kallsyms_offsets_offset);
    }
    if (va_addresses > va_offset) {
        info->kallsyms_addresses_offset = (int32_t)(va_addresses - va_offset);
        tools_logi("System.map -> kallsyms_addresses offset: 0x%08x\n", info->kallsyms_addresses_offset);
    }
    if (va_relative_base) {
        info->kallsyms_relative_base = va_relative_base;
        info->kernel_base = va_relative_base;
        tools_logi("System.map -> kallsyms_relative_base: 0x%016lx\n", (unsigned long)va_relative_base);
    }
    return 0;
}
'''

    target_func = "static int find_token_table(kallsym_t *info, char *img, int32_t imglen, void *opt)"
    if target_func not in content:
        print("[!] target_func find_token_table not found in kallsym.c")
        return False

    content = content.replace(target_func, helper_code + "\n" + target_func)

    token_table_start = """static int find_token_table(kallsym_t *info, char *img, int32_t imglen, void *opt)
{"""
    token_table_hook = """static int find_token_table(kallsym_t *info, char *img, int32_t imglen, void *opt)
{
    load_system_map(info, img, imglen);
    const char *env_tt = getenv("KALLSYMS_TOKEN_TABLE_OFFSET");
    if (env_tt && env_tt[0]) {
        info->kallsyms_token_table_offset = (int32_t)strtoul(env_tt, NULL, 0);
        tools_logi("env -> kallsyms_token_table offset: 0x%08x\\n", info->kallsyms_token_table_offset);
    }
    if (info->kallsyms_token_table_offset > 0) {
        tools_logi("Using verified kallsyms_token_table offset: 0x%08x\\n", info->kallsyms_token_table_offset);
        char *pos = img + info->kallsyms_token_table_offset;
        for (int32_t i = 0; i < KSYM_TOKEN_NUMS; i++) {
            info->kallsyms_token_table[i] = pos;
            while (*(pos++)) {
            };
        }
        return 0;
    }"""
    if token_table_start in content:
        content = content.replace(token_table_start, token_table_hook, 1)

    old_token_index_err = """    if (!lepos && !bepos) {
        tools_loge("kallsyms_token_index error\\n");
        return -1;
    }"""
    new_token_index_err = """    if (!lepos && !bepos) {
        const char *env_ti = getenv("KALLSYMS_TOKEN_INDEX_OFFSET");
        if (env_ti && env_ti[0]) info->kallsyms_token_index_offset = (int32_t)strtoul(env_ti, NULL, 0);
        if (info->kallsyms_token_index_offset > 0) {
            tools_logi("Fallback to verified token_index offset: 0x%08x\\n", info->kallsyms_token_index_offset);
            info->is_be = 0;
            return 0;
        }
        tools_loge("kallsyms_token_index error\\n");
        return -1;
    }"""
    if old_token_index_err in content:
        content = content.replace(old_token_index_err, new_token_index_err, 1)

    old_markers_internal = """static int find_markers_internal(kallsym_t *info, char *img, int32_t imglen, int32_t elem_size)
{
    int32_t cand = info->kallsyms_token_table_offset;"""
    new_markers_internal = """static int find_markers_internal(kallsym_t *info, char *img, int32_t imglen, int32_t elem_size)
{
    const char *env_mo = getenv("KALLSYMS_MARKERS_OFFSET");
    if (env_mo && env_mo[0]) info->kallsyms_markers_offset = (int32_t)strtoul(env_mo, NULL, 0);
    if (info->kallsyms_markers_offset > 0) {
        int32_t cand = info->kallsyms_markers_offset;
        int count = 0;
        int64_t prev = -1;
        while (cand + count * elem_size < imglen) {
            int64_t v = int_unpack(img + cand + count * elem_size, elem_size, info->is_be);
            if (v < prev || (v == 0 && count > 0 && prev > 0)) break;
            prev = v;
            count++;
        }
        if (count >= KSYM_MIN_MARKER) {
            info->_marker_num = count;
            info->kallsyms_markers_elem_size = elem_size;
            tools_logi("kallsyms_markers range from System.map: [0x%08x, 0x%08x), count: 0x%08x\\n",
                       cand, cand + count * elem_size, count);
            return 0;
        }
    }
    int32_t cand = info->kallsyms_token_table_offset;"""
    if old_markers_internal in content:
        content = content.replace(old_markers_internal, new_markers_internal, 1)

    old_find_names = """static int find_names(kallsym_t *info, char *img, int32_t imglen)
{
    int32_t marker_elem_size = get_markers_elem_size(info);"""
    new_find_names = """static int find_names(kallsym_t *info, char *img, int32_t imglen)
{
    const char *env_no = getenv("KALLSYMS_NAMES_OFFSET");
    if (env_no && env_no[0]) info->kallsyms_names_offset = (int32_t)strtoul(env_no, NULL, 0);
    if (info->kallsyms_names_offset > 0) {
        tools_logi("Using verified kallsyms_names offset: 0x%08x\\n", info->kallsyms_names_offset);
        return 0;
    }
    int32_t marker_elem_size = get_markers_elem_size(info);"""
    if old_find_names in content:
        content = content.replace(old_find_names, new_find_names, 1)

    old_find_num_syms = """    for (int32_t cand = approx_end; cand > approx_end - 4096; cand -= num_syms_elem_size) {"""
    new_find_num_syms = """    if (info->kallsyms_num_syms_offset > 0) {
        info->kallsyms_num_syms = (int)int_unpack(img + info->kallsyms_num_syms_offset, num_syms_elem_size, info->is_be);
        tools_logi("Using verified kallsyms_num_syms offset: 0x%08x, value: 0x%08x\\n",
                   info->kallsyms_num_syms_offset, info->kallsyms_num_syms);
        return 0;
    }
    for (int32_t cand = approx_end; cand > approx_end - 4096; cand -= num_syms_elem_size) {"""
    if old_find_num_syms in content:
        content = content.replace(old_find_num_syms, new_find_num_syms, 1)

    with open(kallsym_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("[+] Successfully patched kallsym.c with System.map and env overrides!")
    return True

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "scratch/KernelPatch/tools/kallsym.c"
    patch_kallsym_c(path)
