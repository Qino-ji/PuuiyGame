cbuffer SpriteBuffer : register(b0)
{
    float4x4 Transform;
    float4 Tint;
    float Time;
    float2 TexSize;
};

Texture2D SpriteTexture : register(t0);
SamplerState Sampler : register(s0);

struct VS_INPUT
{
    float3 Position : POSITION;
    float2 TexCoord : TEXCOORD0;
};

struct PS_INPUT
{
    float4 Position : SV_POSITION;
    float2 TexCoord : TEXCOORD0;
};

PS_INPUT VS_Sprite(VS_INPUT input)
{
    PS_INPUT output;
    output.Position = mul(float4(input.Position, 1.0), Transform);
    output.TexCoord = input.TexCoord;
    return output;
}

float4 PS_Sprite(PS_INPUT input) : SV_TARGET
{
    float4 color = SpriteTexture.Sample(Sampler, input.TexCoord);
    return color * Tint;
}

float4 PS_FlipX(PS_INPUT input) : SV_TARGET
{
    float2 uv = float2(1.0 - input.TexCoord.x, input.TexCoord.y);
    float4 color = SpriteTexture.Sample(Sampler, uv);
    return color * Tint;
}

float4 PS_FlipY(PS_INPUT input) : SV_TARGET
{
    float2 uv = float2(input.TexCoord.x, 1.0 - input.TexCoord.y);
    float4 color = SpriteTexture.Sample(Sampler, uv);
    return color * Tint;
}

float4 PS_Rotate90(PS_INPUT input) : SV_TARGET
{
    float2 uv = float2(input.TexCoord.y, 1.0 - input.TexCoord.x);
    float4 color = SpriteTexture.Sample(Sampler, uv);
    return color * Tint;
}

float4 PS_Pulse(PS_INPUT input) : SV_TARGET
{
    float pulse = 0.5 + 0.5 * sin(Time * 3.0);
    float4 color = SpriteTexture.Sample(Sampler, input.TexCoord);
    return color * Tint * pulse;
}

float4 PS_Outline(PS_INPUT input) : SV_TARGET
{
    float2 texel = float2(1.0 / TexSize.x, 1.0 / TexSize.y);
    float4 center = SpriteTexture.Sample(Sampler, input.TexCoord);
    float4 left = SpriteTexture.Sample(Sampler, input.TexCoord + float2(-texel.x, 0));
    float4 right = SpriteTexture.Sample(Sampler, input.TexCoord + float2(texel.x, 0));
    float4 up = SpriteTexture.Sample(Sampler, input.TexCoord + float2(0, -texel.y));
    float4 down = SpriteTexture.Sample(Sampler, input.TexCoord + float2(0, texel.y));
    float outline = 1.0;
    if (center.a > 0.0)
    {
        outline = left.a * right.a * up.a * down.a;
    }
    else
    {
        float maxNeighbor = max(max(left.a, right.a), max(up.a, down.a));
        outline = 1.0 - step(0.5, maxNeighbor);
    }
    return float4(center.rgb, center.a * outline);
}