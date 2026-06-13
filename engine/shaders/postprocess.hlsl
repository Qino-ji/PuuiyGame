cbuffer PostProcessBuffer : register(b0)
{
    float Time;
    float2 Resolution;
    float Intensity;
};

Texture2D SceneTexture : register(t0);
SamplerState Sampler : register(s0);

struct PS_INPUT
{
    float4 Position : SV_POSITION;
    float2 TexCoord : TEXCOORD0;
};

float4 PS_Grayscale(PS_INPUT input) : SV_TARGET
{
    float4 color = SceneTexture.Sample(Sampler, input.TexCoord);
    float gray = dot(color.rgb, float3(0.299, 0.587, 0.114));
    return float4(gray, gray, gray, color.a);
}

float4 PS_Invert(PS_INPUT input) : SV_TARGET
{
    float4 color = SceneTexture.Sample(Sampler, input.TexCoord);
    return float4(1.0 - color.rgb, color.a);
}

float4 PS_Sepia(PS_INPUT input) : SV_TARGET
{
    float4 color = SceneTexture.Sample(Sampler, input.TexCoord);
    float3 sepia;
    sepia.r = dot(color.rgb, float3(0.393, 0.769, 0.189));
    sepia.g = dot(color.rgb, float3(0.349, 0.686, 0.168));
    sepia.b = dot(color.rgb, float3(0.272, 0.534, 0.131));
    return float4(sepia, color.a);
}

float4 PS_Vignette(PS_INPUT input) : SV_TARGET
{
    float4 color = SceneTexture.Sample(Sampler, input.TexCoord);
    float2 uv = input.TexCoord;
    float dist = distance(uv, float2(0.5, 0.5));
    float vignette = smoothstep(0.8, 0.2, dist);
    return float4(color.rgb * vignette, color.a);
}

float4 PS_Chromatic(PS_INPUT input) : SV_TARGET
{
    float offset = Intensity * 0.01;
    float2 uv = input.TexCoord;
    float4 r = SceneTexture.Sample(Sampler, uv + float2(offset, 0.0));
    float4 g = SceneTexture.Sample(Sampler, uv);
    float4 b = SceneTexture.Sample(Sampler, uv - float2(offset, 0.0));
    return float4(r.r, g.g, b.b, g.a);
}

float4 PS_Wave(PS_INPUT input) : SV_TARGET
{
    float2 uv = input.TexCoord;
    uv.x += sin(uv.y * 10.0 + Time * 3.0) * Intensity * 0.01;
    return SceneTexture.Sample(Sampler, uv);
}

float4 PS_Fade(PS_INPUT input) : SV_TARGET
{
    float4 color = SceneTexture.Sample(Sampler, input.TexCoord);
    return float4(color.rgb, color.a * Intensity);
}