#ifndef PUUIY_RENDERER_H
#define PUUIY_RENDERER_H

#include <string>
#include <vector>
#include <map>
#include <cstdint>

struct Color {
    uint8_t r, g, b, a;
    Color() : r(255), g(255), b(255), a(255) {}
    Color(uint8_t r, uint8_t g, uint8_t b, uint8_t a = 255) : r(r), g(g), b(b), a(a) {}
};

struct Vec2 {
    float x, y;
    Vec2() : x(0), y(0) {}
    Vec2(float x, float y) : x(x), y(y) {}
};

struct Rect {
    float x, y, w, h;
    Rect() : x(0), y(0), w(0), h(0) {}
    Rect(float x, float y, float w, float h) : x(x), y(y), w(w), h(h) {}
};

struct Texture {
    int width;
    int height;
    void* data;
    bool loaded;
    Texture() : width(0), height(0), data(nullptr), loaded(false) {}
};

struct SpriteBatch {
    struct Vertex {
        Vec2 position;
        Vec2 texCoord;
        Color color;
    };
    std::vector<Vertex> vertices;
    std::vector<uint32_t> indices;
    int textureId;
    SpriteBatch() : textureId(-1) {}
};

class Renderer {
public:
    Renderer();
    ~Renderer();

    bool init(int width, int height);
    void cleanup();
    void clear();
    void present();

    void set_clear_color(int r, int g, int b);
    void set_offset(float x, float y);
    void set_zoom(float z);
    void set_rotation(float r);

    int load_texture(const std::string& path);
    void free_texture(int id);

    void draw_rect(float x, float y, float w, float h, int r, int g, int b, int a);
    void draw_texture(int tex_id, float x, float y, float w, float h);
    void draw_texture_region(int tex_id, float dx, float dy, float dw, float dh,
                             float sx, float sy, float sw, float sh);
    void draw_text(const std::string& text, float x, float y,
                   const std::string& font, int size, int r, int g, int b);
    void draw_line(float x1, float y1, float x2, float y2,
                   int r, int g, int b, float thickness);
    void draw_circle(float x, float y, float radius, int r, int g, int b, int a);

    void begin_batch();
    void end_batch();

    int get_width() const { return m_width; }
    int get_height() const { return m_height; }
    int get_draw_calls() const { return m_drawCalls; }

private:
    int m_width;
    int m_height;
    int m_clearR, m_clearG, m_clearB;
    float m_offsetX, m_offsetY;
    float m_zoom;
    float m_rotation;
    int m_drawCalls;
    std::map<std::string, Texture> m_textures;
    bool m_running;
};

class Audio {
public:
    Audio();
    ~Audio();

    bool init();
    void cleanup();
    void update();

    int load_sound(const std::string& path);
    int load_music(const std::string& path);
    void play_sfx(int id, float volume);
    void play_music(int id, float volume, bool loop);
    void stop_music();
    void pause_music();
    void resume_music();
    void set_volume(int id, float volume);

private:
    bool m_initialized;
};

class Input {
public:
    bool keys[256];
    bool prevKeys[256];
    bool mouseButtons[8];
    bool prevMouseButtons[8];
    int mouseX, mouseY;
    int mouseWheel;

    Input();
    void poll();
    bool key_down(int key);
    bool key_pressed(int key);
    bool key_released(int key);
    bool mouse_down(int button);
    bool mouse_pressed(int button);
    bool mouse_released(int button);
    int get_mouse_x() const { return mouseX; }
    int get_mouse_y() const { return mouseY; }
};

class Timer {
public:
    static double now();
    static void sleep(double seconds);
};

#endif