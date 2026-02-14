/**
 * OSCE Video Resources Component
 *
 * Displays curated video demonstrations for OSCE physical examination stations
 * with links to trusted medical education sources (Stanford Medicine 25, Geeky Medics, Oxford Medical Education)
 */

import React, { useState } from 'react';
import { VideoResources, VideoResource } from '../types/api';
import {
  ExternalLink,
  PlayCircle,
  Clock,
  Award,
  BookOpen,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

interface OSCEVideoResourcesProps {
  videoResources?: VideoResources;
  stationTitle: string;
}

const VideoResourceCard: React.FC<{ video: VideoResource; category: 'essential' | 'supplementary' }> = ({
  video,
  category
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className={`
      bg-white border rounded-lg shadow-sm hover:shadow-md transition-shadow
      ${category === 'essential' ? 'border-l-4 border-l-blue-500' : 'border-l-4 border-l-gray-300'}
    `}>
      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <PlayCircle className={`w-5 h-5 ${category === 'essential' ? 'text-blue-600' : 'text-gray-600'}`} />
              <h4 className="font-semibold text-gray-900">{video.title}</h4>
            </div>
            <p className="text-sm text-gray-600 mb-2">{video.source}</p>
          </div>
          {video.duration_minutes && (
            <div className="flex items-center gap-1 text-sm text-gray-500 whitespace-nowrap">
              <Clock className="w-4 h-4" />
              <span>{video.duration_minutes} min</span>
            </div>
          )}
        </div>

        {/* Focus Area */}
        <div className="mt-3">
          <div className="flex items-start gap-2 text-sm">
            <BookOpen className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
            <p className="text-gray-700">{video.focus}</p>
          </div>
        </div>

        {/* Why Recommended - Collapsible */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full mt-3 flex items-center justify-between text-sm text-gray-600 hover:text-gray-900"
        >
          <span className="font-medium">Why recommended?</span>
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {isExpanded && (
          <div className="mt-2 text-sm text-gray-700 bg-gray-50 p-3 rounded">
            <p>{video.why_recommended}</p>
            {video.australian_relevance && (
              <div className="mt-2 pt-2 border-t border-gray-200">
                <div className="flex items-start gap-2">
                  <Award className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="font-medium text-green-800 text-xs mb-1">Australian AMC Clinical Exam Relevance</p>
                    <p className="text-gray-700">{video.australian_relevance}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Watch Video Link */}
        <a
          href={video.url}
          target="_blank"
          rel="noopener noreferrer"
          className={`
            mt-3 flex items-center justify-center gap-2 px-4 py-2 rounded-md
            text-white font-medium transition-colors
            ${category === 'essential'
              ? 'bg-blue-600 hover:bg-blue-700'
              : 'bg-gray-600 hover:bg-gray-700'
            }
          `}
        >
          <PlayCircle className="w-4 h-4" />
          <span>Watch Video</span>
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </div>
  );
};

export const OSCEVideoResources: React.FC<OSCEVideoResourcesProps> = ({
  videoResources,
  stationTitle
}) => {
  const [showSupplementary, setShowSupplementary] = useState(false);

  if (!videoResources ||
      (videoResources.essential_videos.length === 0 && videoResources.supplementary_videos.length === 0)) {
    return null;
  }

  const hasEssential = videoResources.essential_videos.length > 0;
  const hasSupplementary = videoResources.supplementary_videos.length > 0;

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-6 my-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="bg-blue-600 p-2 rounded-lg">
            <PlayCircle className="w-6 h-6 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">Video Demonstrations</h3>
        </div>
        <p className="text-gray-700">
          Watch these curated demonstrations from top medical education sources to prepare for your {stationTitle} OSCE station
        </p>
      </div>

      {/* Essential Videos */}
      {hasEssential && (
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-4">
            <div className="bg-blue-100 px-3 py-1 rounded-full">
              <span className="text-sm font-semibold text-blue-800">Essential - Watch These First</span>
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            {videoResources.essential_videos.map((video, index) => (
              <VideoResourceCard
                key={index}
                video={video}
                category="essential"
              />
            ))}
          </div>
        </div>
      )}

      {/* Supplementary Videos - Collapsible */}
      {hasSupplementary && (
        <div>
          <button
            onClick={() => setShowSupplementary(!showSupplementary)}
            className="flex items-center gap-2 mb-4 text-gray-700 hover:text-gray-900 font-medium"
          >
            <div className="bg-gray-100 px-3 py-1 rounded-full">
              <span className="text-sm font-semibold text-gray-700">
                Supplementary Videos ({videoResources.supplementary_videos.length})
              </span>
            </div>
            {showSupplementary ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          </button>

          {showSupplementary && (
            <div className="grid gap-4 md:grid-cols-2">
              {videoResources.supplementary_videos.map((video, index) => (
                <VideoResourceCard
                  key={index}
                  video={video}
                  category="supplementary"
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Footer Note */}
      <div className="mt-6 p-4 bg-white border border-blue-200 rounded-lg">
        <p className="text-sm text-gray-600">
          <strong className="text-gray-900">💡 Study Tip:</strong> Watch videos alongside reading the examination notes.
          Practice the techniques shown, then use our OSCE practice mode to test yourself with the 8-minute timer.
        </p>
      </div>
    </div>
  );
};

export default OSCEVideoResources;
