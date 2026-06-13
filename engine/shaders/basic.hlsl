cbuffer ConstantBuffer : register(b0)
{
    float4x4 WorldViewProjection;
    float4x4 World;
    float4 Tint;
    float Time;
};

Texture2D ShaderTexture : register(t0);
SamplerState Sampler : register(s0);

struct VS_INPUT
{
    float3 Position : POSITION;
    float2 TexCoord : TEXCOORD0;
    float4 Color : COLOR0;
};

struct PS_INPUT
{
    float4 Position : SV_POSITION;
    float2 TexCoord : TEXCOORD0;
    float4 Color : COLOR0;
};

PS_INPUT VS_Main(VS_INPUT input)
{
    PS_INPUT output;
    output.Position = mul(float4(input.Position, 1.0), WorldViewProjection);
    output.TexCoord = input.TexCoord;
    output.Color = input.Color;
    return output;
}

float4 PS_Main(PS_INPUT input) : SV_TARGET
{
    float4 texColor = ShaderTexture.Sample(Sampler, input.TexCoord);
    return texColor * input.Color * Tint;
}