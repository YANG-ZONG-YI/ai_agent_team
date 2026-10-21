import pytest
from src.domain.publish_task import PlatformType
from src.infrastructure.adapters.social_publishers import (
    SocialPublisherFactory,
    PublishResult,
    YouTubeShortsPublisher,
    InstagramReelsPublisher,
    FacebookReelsPublisher,
    TikTokPublisher
)

def test_social_publisher_factory_returns_correct_adapters():
    yt = SocialPublisherFactory.get_publisher(PlatformType.YOUTUBE)
    assert isinstance(yt, YouTubeShortsPublisher)
    
    ig = SocialPublisherFactory.get_publisher(PlatformType.INSTAGRAM)
    assert isinstance(ig, InstagramReelsPublisher)
    
    fb = SocialPublisherFactory.get_publisher(PlatformType.FACEBOOK)
    assert isinstance(fb, FacebookReelsPublisher)
    
    tt = SocialPublisherFactory.get_publisher(PlatformType.TIKTOK)
    assert isinstance(tt, TikTokPublisher)

def test_publish_video_mock_success(tmp_path):
    video_file = tmp_path / "sample.mp4"
    video_file.write_bytes(b"mock video binary")
    
    for platform in [PlatformType.YOUTUBE, PlatformType.INSTAGRAM, PlatformType.FACEBOOK, PlatformType.TIKTOK]:
        publisher = SocialPublisherFactory.get_publisher(platform)
        result = publisher.publish_video(
            title="AI 短影音自動發布測試",
            description="測試各社群發布防腐層",
            video_path=str(video_file)
        )
        assert isinstance(result, PublishResult)
        assert result.success is True
        assert result.platform_video_id is not None
        assert platform.value.lower() in result.platform_video_id
