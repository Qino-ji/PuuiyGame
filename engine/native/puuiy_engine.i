%module puuiy_engine

%{
#include "renderer.h"
%}

%include <std_string.i>
%include <std_vector.i>

struct Color {
    unsigned char r, g, b, a;
    Color();
    Color(unsigned char r, unsigned char g, unsigned char b, unsigned char a = 255);
};

struct Vec2 {
    float x, y;
    Vec2();
    Vec2(float x, float y);
};

struct Rect {
    float x, y, w, h;
    Rect();
    Rect(float x, float y, float w, float h);
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
    int get_width() const;
    int get_height() const;
    int get_draw_calls() const;
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
    int get_mouse_x() const;
    int get_mouse_y() const;
};

class Timer {
public:
    static double now();
    static void sleep(double seconds);
};