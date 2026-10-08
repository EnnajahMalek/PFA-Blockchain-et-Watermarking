import numpy as np
import pywt
from PIL import Image


def embed_bit_in_block(block, bit, alpha=350.0):
    LL, (LH, HL, HH) = pywt.dwt2(block, "haar")
    U, S, Vt = np.linalg.svd(LL)
    quantized = np.floor(S[0] / alpha) * alpha
    if bit == 1:
        S[0] = quantized + 0.75 * alpha
    else:
        S[0] = quantized + 0.25 * alpha
    LL_new = (U * S) @ Vt
    return pywt.idwt2((LL_new, (LH, HL, HH)), "haar")


def extract_bit_from_block(block, alpha=350.0):
    LL, (LH, HL, HH) = pywt.dwt2(block, "haar")
    U, S, Vt = np.linalg.svd(LL)
    remainder = S[0] % alpha
    return 1 if remainder > alpha / 2 else 0


def hex_to_bits(hex_str):
    bits = []
    for byte in bytes.fromhex(hex_str):
        bits.extend([(byte >> i) & 1 for i in range(7, -1, -1)])
    return bits


def bits_to_hex(bits, n_bytes=32):
    byte_vals = []
    for i in range(n_bytes):
        byte_bits = bits[i * 8 : (i + 1) * 8]
        val = 0
        for b in byte_bits:
            val = (val << 1) | b
        byte_vals.append(val)
    return bytes(byte_vals).hex()


def embed_watermark(img, payload_bits, block_size=16, alpha=350.0, seed=424242):
    h, w = img.shape
    blocks_y, blocks_x = h // block_size, w // block_size
    total_blocks = blocks_y * blocks_x
    n_bits = len(payload_bits)

    if total_blocks < n_bits:
        raise ValueError(f"Image too small: {total_blocks} blocks for {n_bits} bits")

    rng = np.random.default_rng(seed)
    block_order = np.arange(total_blocks)
    rng.shuffle(block_order)
    block_to_bit = {b: (i % n_bits) for i, b in enumerate(block_order)}

    watermarked = img.copy()
    for block_idx, bit_idx in block_to_bit.items():
        by, bx = divmod(block_idx, blocks_x)
        y0, x0 = by * block_size, bx * block_size
        block = img[y0 : y0 + block_size, x0 : x0 + block_size]
        wm_block = embed_bit_in_block(block, payload_bits[bit_idx], alpha=alpha)
        watermarked[y0 : y0 + block_size, x0 : x0 + block_size] = wm_block

    return watermarked


def extract_watermark(img, n_bits, block_size=16, alpha=350.0, seed=424242):
    h, w = img.shape
    blocks_y, blocks_x = h // block_size, w // block_size
    total_blocks = blocks_y * blocks_x

    rng = np.random.default_rng(seed)
    block_order = np.arange(total_blocks)
    rng.shuffle(block_order)
    block_to_bit = {b: (i % n_bits) for i, b in enumerate(block_order)}

    votes = {i: [] for i in range(n_bits)}
    for block_idx, bit_idx in block_to_bit.items():
        by, bx = divmod(block_idx, blocks_x)
        y0, x0 = by * block_size, bx * block_size
        block = img[y0 : y0 + block_size, x0 : x0 + block_size]
        votes[bit_idx].append(extract_bit_from_block(block, alpha=alpha))

    recovered = []
    for i in range(n_bits):
        v = votes[i]
        ones = sum(v)
        zeros = len(v) - ones
        recovered.append(1 if ones >= zeros else 0)

    return recovered


def embed_data_in_logo(logo_path, hex_data, output_path):
    img = np.array(Image.open(logo_path).convert("L")).astype(float)
    bits = hex_to_bits(hex_data)
    watermarked = embed_watermark(img, bits)
    watermarked = np.clip(watermarked, 0, 255).astype(np.uint8)
    Image.fromarray(watermarked).save(output_path)
    return output_path


def extract_data_from_logo(logo_path, n_bytes=32):
    img = np.array(Image.open(logo_path).convert("L")).astype(float)
    try:
        n_bits = n_bytes * 8
        recovered_bits = extract_watermark(img, n_bits=n_bits)
        return bits_to_hex(recovered_bits, n_bytes=n_bytes)
    except Exception:
        return None
