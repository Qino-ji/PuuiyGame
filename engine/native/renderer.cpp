#include "renderer.h"
#include <chrono>
#include <thread>
#include <cmath>
#include <algorithm>
#include <cstring>

Renderer::Renderer()
    : m_width(800), m_height(600)
    , m_clearR(20), m_clearG(20), m_clearB(30)
    , m_offsetX(0), m_offsetY(0), m_zoom(1.0f), m_rotation(0)
    , m_drawCalls(0), m_running(false)
{
}

Renderer::~Renderer() {
    cleanup();
}

bool Renderer::init(int width, int height) {
    m_width = width;
    m_height = height;
    m_running = true;
    return true;
}

void Renderer::cleanup() {
    m_textures.clear();
    m_running = false;
}

void Renderer::clear() {
    m_drawCalls = 0;
}

void Renderer::present() {
}

void Renderer::set_clear_color(int r, int g, int b) {
    m_clearR = r;
    m_clearG = g;
    m_clearB = b;
}

void Renderer::set_offset(float x, float y) {
    m_offsetX = x;
    m_offsetY = y;
}

void Renderer::set_zoom(float z) {
    m_zoom = z;
}

void Renderer::set_rotation(float r) {
    m_rotation = r;
}

int Renderer::load_texture(const std::string& path) {
    Texture tex;
    tex.width = 32;
    tex.height = 32;
    tex.loaded = true;
    std::string key = "tex_" + std::to_string(m_textures.size());
    m_textures[key] = tex;
    return static_cast<int>(m_textures.size()) - 1;
}

void Renderer::free_texture(int id) {
}

void Renderer::draw_rect(float x, float y, float w, float h, int r, int g, int b, int a) {
    m_drawCalls++;
}

void Renderer::draw_texture(int tex_id, float x, float y, float w, float h) {
    m_drawCalls++;
}

void Renderer::draw_texture_region(int tex_id, float dx, float dy, float dw, float dh,
                                    float sx, float sy, float sw, float sh) {
    m_drawCalls++;
}

void Renderer::draw_text(const std::string& text, float x, float y,
                          const std::string& font, int size, int r, int g, int b) {
    m_drawCalls++;
}

void Renderer::draw_line(float x1, float y1, float x2, float y2,
                          int r, int g, int b, float thickness) {
    m_drawCalls++;
}

void Renderer::draw_circle(float x, float y, float radius, int r, int g, int b, int a) {
    m_drawCalls++;
}

void Renderer::begin_batch() {
}

void Renderer::end_batch() {
}

Audio::Audio() : m_initialized(false) {
}

Audio::~Audio() {
    cleanup();
}

bool Audio::init() {
    m_initialized = true;
    return true;
}

void Audio::cleanup() {
    m_initialized = false;
}

void Audio::update() {
}

int Audio::load_sound(const std::string& path) {
    return 0;
}

int Audio::load_music(const std::string& path) {
    return 0;
}

void Audio::play_sfx(int id, float volume) {
}

void Audio::play_music(int id, float volume, bool loop) {
}

void Audio::stop_music() {
}

void Audio::pause_music() {
}

void Audio::resume_music() {
}

void Audio::set_volume(int id, float volume) {
}

Input::Input() : mouseX(0), mouseY(0), mouseWheel(0) {
    memset(keys, 0, sizeof(keys));
    memset(prevKeys, 0, sizeof(prevKeys));
    memset(mouseButtons, 0, sizeof(mouseButtons));
    memset(prevMouseButtons, 0, sizeof(prevMouseButtons));
}

void Input::poll() {
    memcpy(prevKeys, keys, sizeof(keys));
    memcpy(prevMouseButtons, mouseButtons, sizeof(mouseButtons));
    mouseWheel = 0;
}

bool Input::key_down(int key) {
    if (key < 0 || key >= 256) return false;
    return keys[key];
}

bool Input::key_pressed(int key) {
    if (key < 0 || key >= 256) return false;
    return keys[key] && !prevKeys[key];
}

bool Input::key_released(int key) {
    if (key < 0 || key >= 256) return false;
    return !keys[key] && prevKeys[key];
}

bool Input::mouse_down(int button) {
    if (button < 0 || button >= 8) return false;
    return mouseButtons[button];
}

bool Input::mouse_pressed(int button) {
    if (button < 0 || button >= 8) return false;
    return mouseButtons[button] && !prevMouseButtons[button];
}

bool Input::mouse_released(int button) {
    if (button < 0 || button >= 8) return false;
    return !mouseButtons[button] && prevMouseButtons[button];
}

double Timer::now() {
    auto tp = std::chrono::high_resolution_clock::now();
    auto duration = tp.time_since_epoch();
    auto millis = std::chrono::duration_cast<std::chrono::milliseconds>(duration).count();
    return static_cast<double>(millis) / 1000.0;
}

void Timer::sleep(double seconds) {
    if (seconds > 0) {
        auto ms = static_cast<int>(seconds * 1000.0);
        std::this_thread::sleep_for(std::chrono::milliseconds(ms));
    }
}